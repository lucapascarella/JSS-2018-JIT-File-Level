# Fine-grained just-in-time defect-prediction

This project contains scripts and data used to re-implemented a faster solution to replicate the work "[Fine-grained just-in-time defect-prediction](https://github.com/lucapascarella/JSS-2018-JIT-File-Level/blob/master/Pascarella_JSS_2018.pdf)" published at the Journal of Systems and Software in 2018.

## NOTES
JIT defect-prediction is based on a pipeline composed of three stages to automatically identify files with defects at commit time through the use of the SZZ algorithm.

1. In the first stage, ```miner-X.py``` creates a list of fixed and bug inducing files.

2. In the second stage, ```metrics-X.py``` calculates the independent variables at file level for each commit.

3. In the third stage, ```classifier-X.py``` trains a Random Forest machine learning model and tests the model with latest commits.

This implementation relies on ad-hoc set of keywords defined per project and on the built-in SZZ algorithm of [pydriller](https://github.com/ishepard/pydriller). A diverse combination of keywords, timespans, and SZZ algorithm may bring to different results. To the best of our knowledge, we selected the most typical representative keywords used by developers to indicate fixes, we approximate the orginal timespan for the new analysis, and we use the built-in SZZ algorithm of [pydriller](https://github.com/ishepard/pydriller).

## Projects
The following table contains the list of 10 projects, the links to GitHub repositories, and the scripts' names used in each stage.

| Project    | Local folder  | GitHub                                                    | Stage 1    | Stage 2      | Stage 3         |
| ---------- |---------------| --------------------------------------------------------- | ---------- | ------------ | --------------- |
| Accumulo   | accumulo      | [Accumulo](https://github.com/apache/accumulo.git)        | miner-0.py | metrics-0.py | classifier-0.py |
| Angular-js | angular.js    | [Angular-js](https://github.com/angular/angular.js.git)   | miner-1.py | metrics-1.py | classifier-1.py |
| Bugzilla   | bugzilla      | [Bugzilla](https://github.com/bugzilla/bugzilla.git)      | miner-2.py | metrics-2.py | classifier-2.py |
| Gerrit     | gerrit        | [Gerrit](https://github.com/gerrit-review/gerrit.git)     | miner-3.py | metrics-3.py | classifier-3.py |
| Gimp       | gimp          | [Gimp](https://github.com/GNOME/gimp.git)                 | miner-4.py | metrics-4.py | classifier-4.py |
| Hadoop     | hadoop        | [Hadoop](https://github.com/apache/hadoop.git)            | miner-5.py | metrics-5.py | classifier-5.py |
| JDeodorant | JDeodorant    | [JDeodorant](https://github.com/tsantalis/JDeodorant.git) | miner-6.py | metrics-6.py | classifier-6.py |
| Jetty      | jetty.project | [Jetty](https://github.com/eclipse/jetty.project.git)     | miner-7.py | metrics-7.py | classifier-7.py |
| JRuby      | jruby         | [JRuby](https://github.com/jruby/jruby.git)               | miner-8.py | metrics-8.py | classifier-8.py |
| OpenJPA    | openjpa       | [OpenJPA](https://github.com/apache/openjpa.git)          | miner-9.py | metrics-9.py | classifier-9.py |

### 1. Preliminary analysis and identification of bug inducting commits 
```miner-X.py``` is a python script designed to collect a preliminary set of information for the given project. Starting from a link to a GitHub repository and a list of keywords used to identify fixes, it clones the remote repository locally and generates two CSV files: ```yyy_bic.csv``` and ```yyy_partial_bic.csv``` where ```yyy``` is the name of the analyzed project.

```yyy_bic.csv``` contains a list of files per commit and a flag in case the commit message represent a fix. Moreover, when a fix is identified for each fixed file in the given commit a corresponding bug inducing commit is assigned.

NOTE 1. A commit can have fixed files and non-fixed files, therefore not all files in a fixed commit are defective (partial defective commits). The identification of defective files relies on git blame, there are cases where it is not possible to blame previous lines, these files are not considered as a fix.

NOTE 2. For the same principle, a bug inducing commit (BIC) does not necessarily introduce defects in every committed file. We identify bug inducing files applying git blame to the modified lines of fixed files.

```yyy_partial_bic.csv``` specifies which files a bug inducing commit (BIC) are actually bug inducing.

The following table summarizes the results obtained running previous scripts:

| Project    | Script     | Commits | Defective commits | Def. partially   | Def. files |
| ---------- | ---------- | ------- | ----------------- | ---------------- | ---------- |
| Accumulo   | miner-0.py | 8639    | 1154              |	39%            |    63%     |
| Angular-js | miner-1.py | 8102    | 2852              |	10%            |    40%     |
| Bugzilla   | miner-2.py | 9250    | 3873              |	35%            |    36%     |
| Gerrit     | miner-3.py | 24340   | 6269              |	29%            |    47%     |
| Gimp       | miner-4.py | 37329   | 8734              |	16%            |    38%     |
| Hadoop     | miner-5.py | 15689   | 2301              |	55%            |    44%     |
| JDeodorant | miner-6.py | 1101    | 348               |	33%            |    43%     |
| Jetty      | miner-7.py | 13784   | 2698              |	34%            |    30%     |
| JRuby      | miner-8.py | 41256   | 9174              |	25%            |    71%     |
| OpenJPA    | miner-9.py | 4263    | 2921              |	21%            |    24%     |

### 2. Independent variables extraction

The second part of this study creates a list of independent variables successively used to train a machine learning algorithm.

```metrics-X.py``` is a python script build for calculating independent variables as listed in Table 2 of the paper.

```extractor.py``` iterates over all commits, tracks file rename, and saves results in ```yyy_metrics.csv``` where ```yyy``` is the name ot the project.

```yyy_metrics.csv``` contains the value of the 24 metrics (COMM, ADEV, DDEV, ADD, DEL, OWN, MINOR, SCTR, NADEV, NDDEV, NCOMM, NSCTR, OEXP, EXP, ND, Entropy, LA, LD, LT, AGE, NUC, CEXP, REXP, SEXP) as defined in Table 2 for each file of the analyzed repository. The pair _git_hash_ and _file_name_ allows identifying to which metric refer a file refers to. While, the two flags _file_buggy_ _file_fix_ specify whether the given file is a fix or a bug inducing.


| Project    | Script       | Unique FIX | Unique BIC | Ref. file FIX               | Ref. file BIC              |
| ---------- | ------------ | ---------- | ---------- | --------------------------- | -------------------------- |
| Accumulo   | metrics-0.py | 479        | 923        |	accumulo_unique_fix.txt     | accumulo_unique_bic.txt    |
| Angular-js | metrics-1.py | 2137       | 2451       | angular.js_unique_fix.txt   | angular.js_unique_fix.txt  |
| Bugzilla   | metrics-2.py | 580        | 744        |	bugzilla_unique_fix.txt     | bugzilla_unique_fix.txt    |
| Gerrit     | metrics-3.py | 3920       | 5504       |	gerrit_unique_fix.txt       | gerrit_unique_fix.txt      |
| Gimp       | metrics-4.py | 7265       | 11417      |	gimp_unique_fix.txt         | gimp_unique_fix.txt        |
| Hadoop     | metrics-5.py | 1879       | 3094       |	hadoop_unique_fix.txt       | hadoop_unique_fix.txt      |
| JDeodorant | metrics-6.py | 350        | 589        |	JDeodorant_unique_fix.txt   | JDeodorant_unique_fix.txt  |
| Jetty      | metrics-7.py | 2926       | 4479       |	jetty_unique_fix.txt        | jetty_unique_fix.txt       |
| JRuby      | metrics-8.py | 8290       | 11915      |	jruby_unique_fix.txt        | jruby_unique_fix.txt       |
| OpenJPA    | metrics-9.py | 2336       | 1803       |	openjpa_unique_fix.txt      | openjpa_unique_fix.txt     |

### 3. Machine learning training and testing

The third part of this study defines a Random Forest machine-learning algorithm. It trains and tests our model for identifying bug inducing commits considering all commits.

| Project    | Script          | Precision | Recall | F-measure | AUC-ROC |
| ---------- | --------------- | ----------| ------ | --------- | ------- | 
| Accumulo   | classifier-0.py | 0.93      | 0.94   | 0.92      | 0.92    |
| Angular-js | classifier-1.py | 0.85      | 0.86   | 0.85      | 0.91    |
| Bugzilla   | classifier-2.py | 0.91      | 0.93   | 0.91      | 0.81    |
| Gerrit     | classifier-3.py | 0.83      | 0.84   | 0.80      | 0.82    |
| Gimp       | classifier-4.py | 0.90      | 0.91   | 0.88      | 0.88    |
| Hadoop     | classifier-5.py | 0.92      | 0.92   | 0.90      | 0.86    |
| JDeodorant | classifier-6.py | 0.77      | 0.90   | 0.77      | 0.76    |
| Jetty      | classifier-7.py | 0.88      | 0.88   | 0.86      | 0.87    |
| JRuby      | classifier-8.py | 0.87      | 0.88   | 0.84      | 0.91    |
| OpenJPA    | classifier-9.py | 0.92      | 0.91   | 0.92      | 0.90    |

Results considering a model with only partially defective commits (Ref. Table 3.5).

| Project    | Script               | Precision | Recall | F-measure | AUC-ROC |
| ---------- | -------------------- | ----------| ------ | --------- | ------- | 
| Accumulo   | classifier-part-0.py | 0.97      | 0.97   | 0.97      | 0.96    |
| Angular-js | classifier-part-1.py | 0.98      | 0.98   | 0.97      | 0.97    |
| Bugzilla   | classifier-part-2.py | 0.97      | 0.97   | 0.97      | 0.86    |
| Gerrit     | classifier-part-3.py | 0.88      | 0.89   | 0.86      | 0.88    |
| Gimp       | classifier-part-4.py | 0.95      | 0.96   | 0.94      | 0.93    |
| Hadoop     | classifier-part-5.py | 0.96      | 0.95   | 0.95      | 0.93    |
| JDeodorant | classifier-part-6.py | 0.65      | 0.64   | 0.63      | 0.70    |
| Jetty      | classifier-part-7.py | 0.94      | 0.94   | 0.92      | 0.93    |
| JRuby      | classifier-part-8.py | 0.83      | 0.85   | 0.81      | 0.89    |
| OpenJPA    | classifier-part-9.py | 0.96      | 0.96   | 0.96      | 0.96    |

Results considering a model with only partially defective commits (Ref. Table 3.6).

| Project    | Script               | Precision | Recall | F-measure | AUC-ROC |
| ---------- | -------------------- | ----------| ------ | --------- | ------- | 
| Accumulo   | classifier-full-0.py | 0.82      | 0.82   | 0.80      | 0.83    |
| Angular-js | classifier-full-1.py | 0.79      | 0.79   | 0.79      | 0.87    |
| Bugzilla   | classifier-full-2.py | 0.90      | 0.90   | 0.89      | 0.84    |
| Gerrit     | classifier-full-3.py | 0.78      | 0.79   | 0.76      | 0.81    |
| Gimp       | classifier-full-4.py | 0.79      | 0.81   | 0.78      | 0.82    |
| Hadoop     | classifier-full-5.py | 0.85      | 0.86   | 0.85      | 0.90    |
| JDeodorant | classifier-full-6.py | 0.87      | 0.91   | 0.88      | 0.84    |
| Jetty      | classifier-full-7.py | 0.75      | 0.75   | 0.74      | 0.80    |
| JRuby      | classifier-full-8.py | 0.79      | 0.80   | 0.79      | 0.82    |
| OpenJPA    | classifier-full-9.py | 0.89      | 0.88   | 0.88      | 0.91    |

## USAGE

### Cold start
To run all scripts from scratch on a 40 cores machine we took 4 weeks. Therefore, if yuo want save time just clone the repository, skip this part, and focus on ```warm start```.

Clone the repository on your local machine ```git clone https://github.com/lucapascarella/JSS-2018-JIT-File-Level.git```

Create project folder ```mkdir projects```

### Warm start
For a fast run, you can use our previously extracted metrics. ```data``` contains two archives with all metrics already extracted.

Use the following commands to extract and move metrics data:

Extract CSV files ```tar -xzvf data/csv.tar.gz```

Extract TXT files ```tar -xzvf data/txt.tar.gz```

Move extracted data into root ```mv data/projects/* projects```


### Create a virtual environment and install requirements

Create virtual environment ```python3 -m venv venv```

Activate virtual environment ```source venv/bin/activate```

Upgrade pip ```pip install --upgrade pip```

Install requirements ```pip install -r requirements.txt```

### Clone and mine repositories

Change working directory ```cd miner```

Run script (e.g., JDeodorant) ```python3 miner-6.py```

Repeat the above step for every project you want to analyze.

Return to root-project working directory ```cd ..```

### Extract metrics (independent variables)

Change directory ```cd metrics```

Run script (e.g., JDeodorant) ```python3 metrics-6.py```

Repeat the above step for every project you want to analyze.

Change working directory ```cd ..```

### Run main classifier (include both partially and fully defective commits)

Change directory ```cd classifier```

Run script (e.g., JDeodorant) ```python3 classifier-6.py```

Repeat the above step for every project you want to analyze.

Change working directory ```cd ..```

### Run other classifiers (partially or fully defective commits only)

To run our scripts on a reduced set of commits, including exclusively partially or fully defective commits only you must change the working directory and invoke the right scripts.
This example is for _JDeodorant_ only which is the smallest (fastest) project to analyze.

#### Partially defective only
Change directory ```cd classifier-partial```

Run script (e.g., JDeodorant) ```python3 classifier-part-6.py```

Repeat the above step for every project you want to analyze.

Change working directory ```cd ..```

#### Fully defective only
Change directory ```cd classifier-fully```

Run script (e.g., JDeodorant) ```python3 classifier-full-6.py```

Repeat the above step for every project you want to analyze.

Change working directory ```cd ..```

## RQ3 – Investigating the importance of the features

While in RQ2 we provide an overview of the accuracy of the proposed model in predicting defective files at commit level, RQ3 investigates which features contribute the most to the prediction capabilities.
We anwsered the third research question by using Weka tool, and in particular the InfoGainAttributeEval option.

To generate the coumns of Table 3.7, we performed the analysis by projects.

1. Start Weka GUI tool, we used version 3.8.3. 
2. Select "Explorer" button.
3. Click on "Open file ..." button and select one of the ten <project>_metrics.csv file.
4. Remove unwanted columns that are not features as in Fig. XX. You must obtain a list of features as in Fig. XX   
5. Move to "Select attributes" tab, click on "Choose" button and select InfoFainAttributeEval.
6. Click on "Start" button and wait for the final rank as shown in Fig 3.
7. Repeat from step 3 for the other projects.

Fig 1. ![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")
Fig 2. ![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")
Fig 3. ![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")

## License
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
 
[https://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0)
 
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

<!--- ### References
 (Sponsor: [LPSystems B.V.](https://lpsystems.eu/)
Author: [Luca Pascarella](https://lucapascarella.com/)
Co-authors: [Fabio Palomba](https://dibt.unimol.it/staff/fpalomba/) and [Alberto Bacchelli](https://sback.it/)

### Acknowledgment
[Alberto Bacchelli](https://sback.it/) and [Fabio Palomba](https://dibt.unimol.it/staff/fpalomba/) gratefully acknowledge the support of the Swiss National Science Foundation through the SNF Projects No. PP00P2_170529 and No. PZ00P2_186090 for the work related the paper JSS-2018. Moreover, the work done in the original project has received funding from the European Union's H2020 programme under the Marie Sklodowska-Curie grant agreement No 642954. Finally, the current replication study has been built entirely by [Luca Pascarella](https://lucapascarella.com/) and funded by [LPSystems B.V.](https://lpsystems.eu/) -->
