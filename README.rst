Census Extract
==============

The scripts in this python module will upload an Ambry bundle for a release of the Amberican Community Survey to a directory or S3 bucket as CSV files, with one file per summary level per table. The file will also include columns for the non-null values from the geofile. 

To run these scripts, you must first [install Ambry](http://docs.ambry.io/) and configure it with the ACS bundle remote, and a remote for the CSV files to be written to. 

However, most users should just use the CSV files that are already written to a public S3 bucket. 

Using The Public S3 Files
*************************


Running the Scripts
*******************

To run these scripts, you must: 

# [Install Ambry](http://docs.ambry.io/)
# Add a remote for the census bundles
# Sync the census bundles
# Create a remote to write the CSV files to

Install Ambry
-------------

The [Ambry installation guide](http://docs.ambry.io/) has details for many platforms, but if you are writing to S3, you'll probably want to create a new Amazon S3 instance. In that case, create a new Ubuntu 14.04 instance, and then you can run this: 

.. code-block:: bash

    $ sudo apt-get update && sudo apt-get install -y curl && \
    sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/CivicKnowledge/ambry/master/support/install/install-ubuntu-14.04.sh)"


Add Census Remote
-----------------

After installing Ambry, you should be able to run :command:`ambry info` to get the configuration information. The line for 'Config:' shows the location of your configuration file, and in the same directory, you can create a configuration for remotes, which holds information about 

.. code-block:: yaml

    remotes:
        census:
            service: http
            url: https://s3.amazonaws.com/census.public.civicknowledge.com/

Then run :command:`ambry info` to cause the remotes to be reloaded. You should see 'census' in the 'remotes' section. 

Sync Census Bundles
-------------------

To sync the census bundles, run :command:`ambry sync census`. It should run for a few minutes, and when it is done, :command:`ambry list` should show census bundles. 

.. code-block:: bash

    $ ambry list 
    ambry list 
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

Add one or both of these two inner blocks to your :file:`remotes.yaml` file.

.. code-block:: yaml

    remotes:
        census-dest-fs:
            service: fs
            url: /Volumes/DataLibrary/cache/census
        census-dest-s3:
            service: fs
            url: https://s3.amazonaws.com/census.public.civicknowledge.com/

So your final :file:`remotes.yaml` might look like this, if you add both:

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
            access: XGL3FAAKIEV6AI3LPMGD
            secret: E55i6oBwrqNfqLHIXHWmR+jXRl1B+nvEclXJeN5l
            url: s3://extracts.census.civicknowledge.com

Then, run :command:`ambry info` to re-load the remotes. 
