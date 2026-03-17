python ../deeper_null/fit_model.py \
    --covar_file ../data/dev/covariates_with_scaled_emb_named.tsv \
    --pheno_file ../data/dev/phenotype_0_5.tsv \
    --model_config ../data/dev/lin_config.json \
    --out_dir test_out/lin \
    --train_samples ../data/dev/train_samples.txt \
    --pred_samples ../data/dev/val_samples.txt ../data/dev/test_samples.txt