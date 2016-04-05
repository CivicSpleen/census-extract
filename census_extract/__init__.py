def main(argsv):
    from cli import make_parser

    parser = make_parser(argsv[0])

    args = parser.parse_args(argsv[1:])

    args.command(args)


def get_geo(geofile_b, release, sl):
    from operator import itemgetter
    """Return the geo rows, indexed to the stusab and logrecno, for a summary level"""
    from collections import OrderedDict

    if not hasattr(geofile_b, '_census_geo'):
        geofile_b._census_geo = {}

    geo = geofile_b._census_geo

    if sl in geo:
        return geo[sl]

    d = {}

    geo_p = geofile_b.partition(grain=str(sl), time='{}{}'.format(geofile_b.identity.btime, release))

    geo_p.localize()

    ig = None
    col_dicts = None

    for row in geo_p:

        if not ig:
            cols = ([u'stusab', u'logrecno', u'geoid'] +
                    [k for k in row.keys() if k not in ('id', 'stusab', 'fileid', 'sumlevel', 'component',
                                                        'logrecno', 'geoid')])
            ig = itemgetter(*cols)
            col_dicts = [geo_p.table.column(c).dict for c in cols]

        d["{}/{}".format(row.stusab.lower(), row.logrecno)] = OrderedDict(zip(cols, ig(row)))

    geo[sl] = (d, col_dicts)

    return geo[sl]


def write_schema(table, geo_cols, acs_cols, dir_, remote):
    import unicodecsv as csv
    from operator import itemgetter
    from os.path import join

    header = ('name', 'schema_type', 'description')

    ig = itemgetter(*header)

    file_name = join(dir_, '{}-schema.csv'.format(table))

    with remote.fs.open(file_name, 'wb') as f:
        w = csv.writer(f)

        w.writerow(('position',) + header)

        for i, e in enumerate(geo_cols + acs_cols, 1):
            w.writerow((i,) + ig(e))


def write_csv(library, ref, remote_name=None, multi=True, raise_exc=False):
    """
    Write CSV extracts to a remote
    :param library:
    :param ref:
    :param remote_name:
    :param multi:
    :param raise_exc:
    :return:
    """

    remote_name = remote_name or 'census-extracts'
    b = library.bundle(ref)

    multi = library.dsn.startswith('post')

    if multi:

        from multiprocessing import Pool

        library.close()

        pool = Pool()

        args = [(remote_name, b.identity.vid, p.vid, raise_exc) for p in b.partitions]
        library.close()
        b.close()

        pool.map(write_partition_csv_mp, args)

    else:

        remote = library.remote(remote_name)

        for p in b.partitions:
            try:
                write_partition_csv(library, remote, b, p)
            except Exception as e:
                library.logger.error(e)
                if raise_exc:
                    raise


def write_partition_csv_mp(args):
    from ambry import get_library
    remote_name, b_ref, p_ref, raise_exc = args

    library = get_library()
    remote = library.remote(remote_name)
    b = library.bundle(b_ref)
    p = library.partition(p_ref)

    try:
        write_partition_csv(library, remote, b, p)
    except Exception as e:
        library.logger.error(e)
        if raise_exc:
            raise


def write_sumlevels(remote, year, release, file_name, sl_names):
    """Write a json file of all of the available summary levels. """
    from json import loads, dumps

    file_name = "{}/{}/sumlevels.json".format(year, release)

    if remote.fs.exists(file_name):
        names = set(loads(remote.fs.getcontents(file_name)))
    else:
        names = set()

    names |= sl_names

    remote.fs.setcontents(file_name, dumps(sorted(names)))


def write_partition_csv(library, remote, b, p):
    from collections import defaultdict
    import unicodecsv as csv
    from os.path import dirname
    from operator import itemgetter
    from geoid import names as geo_names

    geo_names_map = { v:k for k,v in geo_names.items()}

    used_names = set()

    delete_when_finished = False

    year = b.identity.btime[-4:]
    release = b.identity.btime[1:2]

    geofile_b = library.bundle("census.gov-acs-geofile-{}".format(year))

    sum_levels = set([int(pp.identity.grain) for pp in geofile_b.partitions
                      if pp.identity.grain and pp.identity.time == "{}{}".format(year, release)
                      and int(pp.identity.grain) not in (10, 20, 30, 250, 335, 350, 355)
                      ])  # summary levels

    rows = defaultdict(list)

    table_name = p.table.name

    library.logger.info('Loading: {}'.format(p.vname))


    cols = ([u'stusab', u'logrecno'] + [unicode(c.name) for c in p.table.columns if c.name not in
                                        ('id', 'stusab', 'sequence', 'logrecno', 'gvid', 'sumlevel', 'jam_flags',
                                         'geoid')])

    ig = itemgetter(*cols)

    for n, sumlevel in enumerate(sorted(sum_levels)):

        sl_name = "{}_{}".format(sumlevel, geo_names_map[sumlevel])

        used_names.add(sl_name)

        file_name = "{}/{}/{}/{}.csv".format(year, release, sl_name, table_name)

        if remote.fs.exists(file_name):
            library.logger.info("{} exists, skipping".format(file_name))
            continue

        if not rows:

            # Can't use http service to access remote datafiles, because the MPR file code requires tell()
            if not p.is_local and p.remote.url.startswith('http'):
                library.logger.info('Localizing: {}'.format(p.vname))
                p.localize()
                delete_when_finished = True

            library.logger.info("Loading rows")
            for row in p:
                rows[row.sumlevel].append(ig(row))

            library.logger.info("Loaded rows for {} summary levels".format(len(rows)))

        geo, geo_col_dicts = get_geo(geofile_b, release, sumlevel)

        dir_ = dirname(file_name)

        remote.fs.makedir(dir_, recursive=True, allow_recreate=True)

        if len(rows[sumlevel]) == 0:
            library.logger.info("File {} would have no rows, skipping".format(file_name))
            continue

        library.logger.info('Writing {} {} {}'.format(n, file_name, len(rows[sumlevel])))

        geocols = geo[geo.keys()[0]].keys()


        with remote.fs.open(file_name, 'wb') as f:
            w = csv.writer(f)

            for i, row in enumerate(rows[sumlevel]):

                geo_key = "{}/{}".format(row[0], row[1])
                geo_row = geo[geo_key]

                if i == 0:
                    write_schema(table_name, geo_col_dicts, [p.table.column(c).dict for c in cols[2:]],
                                 dir_, remote)

                    w.writerow(geocols + cols[2:])

                w.writerow(tuple(geo_row.values()) + row[2:])

    write_sumlevels(remote, year, release, file_name, used_names)


    if delete_when_finished:
        library.logger.info('Removing localized partition: {}'.format(p.vname))
        p.datafile.remove()