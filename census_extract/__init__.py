
def main(argsv):

    from cli import make_parser

    parser = make_parser(argsv[0])

    args = parser.parse_args(argsv)

    args.command(args)

def write_csv(self):
    """Write CSV extracts to a remote"""
    from collections import defaultdict
    import csv

    remote = self.library.remote('census-extracts')
    s3 = remote.fs

    year = self.year
    release = self.release

    for p in self.partitions:

        rows = defaultdict(list)

        table_name = p.table.name

        self.log('Loading: {} {} {}'.format(year, release, table_name))
        p.localize()

        for i, row in enumerate(p):
            rows[row.sumlevel].append(row.values())

            if i > 100:
                break

        for i, sumlevel in enumerate(sorted(rows.keys())):
            sl_rows = rows[sumlevel]

            file_name = "{}/{}/{}/{}.csv".format(year, release, table_name, sumlevel)
            self.log('Writing {} {} {}'.format(i, file_name, len(sl_rows)))

            with s3.open(file_name, 'wb') as f:
                w = csv.writer(f)

                w.writerow([unicode(c.name) for c in p.table.columns])
                for row in sl_rows:
                    w.writerow(row)