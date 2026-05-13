This ML model is trained on my BCBP DB made for the ERD, Sianquita's tables are different.

Revise/Tweak classification into a scoring/ranking style and just display it by highest to lowest score or something. 
Pivot from hard yes/no eligibility to degree/scale of eligiblity. 

Add noise based on reasonable assumptions (even w/o consultations) to make the synthetic dataset less >deterministic<, !not realistically calibrated!. 
Present / word as "variablity injectiion".

Should be done in wed/thurs.

Wednesday Update Notes: "realistic" "Noise" in sample dataset(csv) is added, as well as CV (cross-validation). model is still conservative for who is eligible. 
The new rf model's recall % tanked but precision is still "100%", since its now a degree of eligiblity, no hard yes/no, fair enough.
Taking note of the tested 63%~ recall means it avoids possibly incorrect reccomendations (false+) at the cost of missing some borderline eligible members (false-).

TLDR:  Accuracy - overall correctness of predictions (eligible or not), v2 model is mostly correct | overall correctness of the model
       Precision - of all predicted eligible members, how many are actually eligible (no false positives) | model is very strict but a reliable decision helper
       Recall - of all truly eligible members, only ~63% are correctly identified by v2 model (37% missed / false negatives) 
       Cross-Validation Accuracy (5-fold) – ~95% average accuracy across 5 different train/test splits, 
                                            showing the model is stable and consistent over multiple trainings/testings. (only v2 model has C-V A)

CV Example: Split 500 records into 5 equal groups  of 100 records each. (current setup of v2 model)
    Round 1: Train on groups 2,3,4,5 → Test on group 1
    Round 2: Train on groups 1,3,4,5 → Test on group 2
    Round 3: Train on groups 1,2,4,5 → Test on group 3
    Round 4: Train on groups 1,2,3,5 → Test on group 4
    Round 5: Train on groups 1,2,3,4 → Test on group 5

    Average all 5 accuracy scores → final CV accuracy
