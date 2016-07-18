Census Extract
==============

The scripts in this python module will upload an Ambry bundle for a release of the Amberican Community Survey to a directory or S3 bucket as CSV files, with one file per summary level per table. The file will also include columns for the non-null values from the geofile. 

To run these scripts, you must first [install Ambry](http://docs.ambry.io/) and configure it with the ACS bundle remote, and a remote for the CSV files to be written to. However, most users should just use the CSV files that are already written to a public S3 bucket. 

Using The Public S3 Files
*************************

The easiest way to explore the file collection is through the bucket explorer, which is avilable at the URL: 

    https://s3.amazonaws.com/extracts.census.civicknowledge.com/index.html
    
    
The URL structure for files is: 

    <year>/<release_span>/<summary_level>/<table>.csv  

The path components are: 

* year. The year of the ACS release
* release_span. The release span in years, 5, 3 or 1 for releases prior to 2014, 5 or 1 after. 
* summary_level. A name that combines the summary level number with a short name. See the next section for possible values. 
* table. The name of the table. 

Additionally, every summary level has a CSV file for a data dictionary, at ``<table>-schema.csv``



Summary Level Path Component
----------------------------

1 Year Release Summary Level Names
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===============  =====================  ===================================================
  Summary Level  Path Component         Description
===============  =====================  ===================================================
             40  40_state               State
             50  50_county              County
             60  60_cosub               County Subdivision
            160  160_place              Place
            230  230_state_anrc         State-Alaska Native Regional Corporation
            310  310_cbsa               CBSA
            312  312_cbsa_state_place   CBSA-State-Principal City
            330  330_csa                Combined Statistical Area
            352  352_necta_state_place  New England City and Town Area-State-Principal City
            400  400_ua                 Urban Area,
            500  500_cdcurr             Congressional District
            795  795_state_puma5        State-Public Use MicroSample Area 5%
            950  950_sdelm              State-Elementary School District
            960  960_sdsec              State-High School District
            970  970_sduni              State-Unified School District
===============  =====================  ===================================================


Running the Scripts
*******************

To run these scripts, you must: 

1. [Install Ambry](http://docs.ambry.io/)
2. Add a remote for the census bundles
3. Sync the census bundles
4. Create a remote to write the CSV files to
5. Install the census-extract python package
6. Run the census-extract program

Install Ambry
-------------

The [Ambry installation guide](http://docs.ambry.io/) has details for many platforms, but if you are writing to S3, you'll probably want to create a new Amazon S3 instance. In that case, create a new Ubuntu 14.04 instance, and then you can run this: 

.. code-block:: bash

    $ sudo apt-get update && sudo apt-get install -y curl && \
    sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/CivicKnowledge/ambry/master/support/install/install-ubuntu-14.04.sh)"


Add Census Remote
-----------------

After installing Ambry, you should be able to run ``ambry info`` to get the configuration information. The line for 'Config:' shows the location of your configuration file, and in the same directory, you can create a configuration for remotes, which holds information about 

.. code-block:: yaml

    remotes:
        census:
            service: http
            url: https://s3.amazonaws.com/census.public.civicknowledge.com/

Then run ``ambry info`` to cause the remotes to be reloaded. You should see 'census' in the 'remotes' section. 

Sync Census Bundles
-------------------

To sync the census bundles, run ``ambry sync census``. It should run for a few minutes, and when it is done, ``ambry list`` should show census bundles. 

.. code-block:: bash

    $ ambry list 

    vid      vname                                       dstate        bstate  about.title                             
    -------  ------------------------------------------  ----------  --------  --------------------------------------  
    d04w002  census.gov-acs-geofile-2009-0.0.2           checkedout            American Community Survey Geofile 2009  
    d057001  census.gov-acs-geofile-2013-0.0.1           checkedout            American Community Survey Geofile 2013  
    d04S002  census.gov-acs-geofile-2014-0.0.2           checkedout            American Community Survey Geofile 2014 
    d052002  census.gov-acs-p1ye2014-0.0.2               checkedout            2014 1 Year ACS                         
    d04T001  census.gov-acs-p5ye2014-0.0.1               checkedout            2014 5 Year ACS                         
    d04s002  census.gov-acs_geofile-schemas-2009e-0.0.2  checkedout            ACS Geofile Schema Definitions          
    d04s003  census.gov-acs_geofile-schemas-2009e-0.0.3  checkedout            ACS Geofile Schema Definitions          
    
Hopefully, the bundles for the ACS years you want are in the list. For each year, you will also need the associated geofile bundle. 


Create remote for Destination
-----------------------------

Finally, you should create a remote entrry for the destination of the CSV file. This could either be a local file system, or an S3 bucket. 

Add one or both of these two inner blocks to your ``remotes.yaml`` file.

.. code-block:: yaml

    remotes:
        census-dest-fs:
            service: fs
            url: /Volumes/DataLibrary/cache/census
        census-dest-s3:
            service: fs
            url: https://s3.amazonaws.com/census.public.civicknowledge.com/

So your final :file:``remotes.yaml`` might look like this, if you add both:

.. code-block:: yaml

    remotes:
        census:
            service: http
            url: https://s3.amazonaws.com/census.public.civicknowledge.com/
        census-dest-fs:
            service: fs
            url: /tmp/census
        census-dest-s3:
            service: s3
            access: <your access key>
            secret: <your secret key>
            url: s3://extracts.census.civicknowledge.com

Then, run :command:``ambry info`` to re-load the remotes. 

Install census-extract
----------------------

.. code-block:: bash

    pip install git+https://github.com/CivicKnowledge/census-extract.git


Run The Census-extract program
------------------------------

First, list the ambry bundles with ``ambry list`` to get the reference name to an ACS bundle. The bundle should have a name like ``census.gov-acs-p1ye2014-0.0.2``. Then, run the ``census-extract`` program with the name. 

Run ``census-extract run -h`` for command options. 


.. code-block:: bash

    census-extract run census.gov-acs-p1ye2014 -r census-dest-s3 -e -m



