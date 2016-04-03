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


