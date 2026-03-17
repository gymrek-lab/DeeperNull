python ../deeper_null/get_shapley_values.py \
    --model_files test_out/xgb/model_0.json test_out/xgb/model_1.json \
    --covar_file ../data/dev/covariates_with_scaled_emb_named.tsv \
    --pred_samples ../data/dev/test_samples.txt \
    --model_type xgb \
    --out_dir test_out/shap