# Dashboarding Project

## By: Brandon Hampstead and Lily Hoffman

Dataset is from the Lahman's Baseball dataset located on [data.world](https://data.world/bgadoci/lahmans-baseball-database)

Our dashboard uses three tables, two from the Baseball Dataset, and one that is a reference table for statistics and their explinations.

In ```data/``` there are three CSV files that are used to load the data to their respective tables, based off the CSV name.

The teams table is a collection of season statistics for ```teams``` ranging the years of 1880 to 2015. The `team_franchises` table is a record of baseball franchises and is used to match franchID to teamID in the `teams` table.

The teams_columns_mapping table contains the column names of showable statistics matched with a description of what they are. This is used in the dashboard dropdown for Statistics so that the user can know what stat they are choosing to look at.

The `generate_baseball_db.py` is a script that takes the CSV files in `data/` and transforms them into the tables in the `baseball.db` database file.

Our dashboard can be run from the `baseball.py` file.

