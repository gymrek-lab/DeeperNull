"""For significantly different PGS models, count directions of difference."""

import os

import pandas as pd


COVAR_MAP = {
	'age_sex_all_coords_pc': 'age, sex, locations', 
	'age_sex_time_pc': 'age, sex, times',
	'age_sex_all_coords_time_pc': 'age, sex, locations, times',
	'age_sex_all_coords_pc_null_xgb_3_age_sex_all_coords': 'age, sex, locations',
	'age_sex_time_pc_null_xgb_3_age_sex_time': 'age, sex, times',
	'age_sex_all_coords_time_pc_null_xgb_3_age_sex_all_coords_time': 'age, sex, locations, times',
	'age_sex_all_coords_time_pc_null_xgb_3_age_sex_all_coords_time_pc': 'age, sex, locations, times, PCs for null',
	'age_sex_pc_null_xgb_3_age_sex': 'age, sex',
	'age_sex_all_coords_pc_null_xgb_3_bin_cls_age_sex_all_coords': 'age, sex, locations',
	'age_sex_all_coords_time_pc_null_xgb_3_bin_cls_age_sex_all_coords_time': 'age, sex, locations, times',
	'age_sex_all_coords_time_pc_null_xgb_3_bin_cls_age_sex_all_coords_time_pc': 'age, sex, locations, times, PCs for null'
}


if __name__ == "__main__":

	# Load pairwise comparison results
	paired_res_dir = 'fisher_pitman_paired'
	paired_res_fname = 'merged_paired_results.csv'

	paired_df = pd.read_csv(os.path.join(paired_res_dir, paired_res_fname))

	print(f"Total comparisons: {len(paired_df)}")
	print(f"BASIL classification comparisons: {(paired_df['model'] == 'BASIL classification').sum()}")
	print(f"BASIL regression comparisons: {(paired_df['model'] == 'BASIL regression').sum()}")
	print(f"PRS-CS regression comparisons: {(paired_df['model'] == 'PRS-CS regression').sum()}")

	# Correct p-values for multiple testing (Bonferroni correction)
	paired_df['p-val_bonf_corrected'] = paired_df['p-val'] * len(paired_df)

	# Filter to significant comparisons
	p_thresh = 0.01
	paired_df = paired_df[paired_df['p-val_bonf_corrected'] < p_thresh]

	print(
		f"Comparisons with Bonferroni-corrected p < {p_thresh}: {len(paired_df)}"
	)

	# Load scores tables to get direction of difference
	scores_df = pd.read_csv('sup_table/sup_table_results_long.csv')


	# First do BASIL classification
	basil_cls_df = paired_df[paired_df['model'] == 'BASIL classification']

	# Add baseline score from scores table to basil_cls_df
	basil_cls_df.loc[:, 'baseline_score'] = None

	for pheno in basil_cls_df['pheno'].unique():
		baseline_score = scores_df[
			(scores_df['pheno'] == pheno)
			& (scores_df['model_type'] == 'BASIL')
			& (scores_df['covar_set'] == 'age, sex')
			& (scores_df['metric'] == 'average_precision')
			& (scores_df['uses_null'] == False)
		]

		assert len(baseline_score) == 1, f"Expected exactly one baseline score for {pheno}, got {len(baseline_score)}"

		baseline_score = baseline_score['value'].item()
		basil_cls_df.loc[
			basil_cls_df['pheno'] == pheno, 'baseline_score'
		] = baseline_score

	# Add alternative score from paired_df to basil_cls_df
	basil_cls_df.loc[:, 'alternative_score'] = None

	for idx, row in basil_cls_df.iterrows():
		pheno = row['pheno']

		uses_null = 'xgb' in row.covars

		alternative_score = scores_df[
			(scores_df['pheno'] == pheno)
			& (scores_df['model_type'] == 'BASIL')
			& (scores_df['metric'] == 'average_precision')
			& (scores_df['uses_null'] == uses_null)
			& (scores_df['covar_set'] == COVAR_MAP[row.covars])
		]

		assert len(alternative_score) == 1, f"Expected exactly one alternative score for {pheno} and {row}, got {len(alternative_score)}"

		alternative_score = alternative_score['value'].item()
		basil_cls_df.loc[idx, 'alternative_score'] = alternative_score

	
	# Create df for BASIL regression in same way
	basil_reg_df = paired_df[paired_df['model'] == 'BASIL regression']
	basil_reg_df.loc[:, 'baseline_score'] = None
	basil_reg_df.loc[:, 'alternative_score'] = None

	for pheno in basil_reg_df['pheno'].unique():
		baseline_score = scores_df[
			(scores_df['pheno'] == pheno)
			& (scores_df['model_type'] == 'BASIL')
			& (scores_df['covar_set'] == 'age, sex')
			& (scores_df['metric'] == 'r2')
			& (scores_df['uses_null'] == False)
		]

		assert len(baseline_score) == 1, f"Expected exactly one baseline score for {pheno}, got {len(baseline_score)}"

		baseline_score = baseline_score['value'].item()
		basil_reg_df.loc[
			basil_reg_df['pheno'] == pheno, 'baseline_score'
		] = baseline_score

	for idx, row in basil_reg_df.iterrows():
		pheno = row['pheno']

		uses_null = 'xgb' in row.covars

		alternative_score = scores_df[
			(scores_df['pheno'] == pheno)
			& (scores_df['model_type'] == 'BASIL')
			& (scores_df['metric'] == 'r2')
			& (scores_df['uses_null'] == uses_null)
			& (scores_df['covar_set'] == COVAR_MAP[row.covars])
		]

		assert len(alternative_score) == 1, f"Expected exactly one alternative score for {pheno} and {row}, got {len(alternative_score)}"

		alternative_score = alternative_score['value'].item()
		basil_reg_df.loc[idx, 'alternative_score'] = alternative_score


	# Now PRS-CS regression
	prscs_reg_df = paired_df[paired_df['model'] == 'PRS-CS regression']
	prscs_reg_df.loc[:, 'baseline_score'] = None
	prscs_reg_df.loc[:, 'alternative_score'] = None

	for pheno in prscs_reg_df['pheno'].unique():
		baseline_score = scores_df[
			(scores_df['pheno'] == pheno)
			& (scores_df['model_type'] == 'PRScs')
			& (scores_df['covar_set'] == 'age, sex')
			& (scores_df['metric'] == 'r2')
			& (scores_df['uses_null'] == False)
		]

		assert len(baseline_score) == 1, f"Expected exactly one baseline score for {pheno}, got {len(baseline_score)}"

		baseline_score = baseline_score['value'].item()
		prscs_reg_df.loc[
			prscs_reg_df['pheno'] == pheno, 'baseline_score'
		] = baseline_score

	for idx, row in prscs_reg_df.iterrows():
		pheno = row['pheno']

		uses_null = 'xgb' in row.covars

		alternative_score = scores_df[
			(scores_df['pheno'] == pheno)
			& (scores_df['model_type'] == 'PRScs')
			& (scores_df['metric'] == 'r2')
			& (scores_df['uses_null'] == uses_null)
			& (scores_df['covar_set'] == COVAR_MAP[row.covars])
		]

		assert len(alternative_score) == 1, f"Expected exactly one alternative score for {pheno} and {row}, got {len(alternative_score)}"

		alternative_score = alternative_score['value'].item()
		prscs_reg_df.loc[idx, 'alternative_score'] = alternative_score


	# Print counts where alternative is better vs. baseline for each model
	print("BASIL classification:")
	print(f"Alternative better than baseline: {(basil_cls_df['alternative_score'] > basil_cls_df['baseline_score']).sum()}")
	print(f"Baseline better than alternative: {(basil_cls_df['alternative_score'] < basil_cls_df['baseline_score']).sum()}")

	print("BASIL regression:")
	print(f"Alternative better than baseline: {(basil_reg_df['alternative_score'] > basil_reg_df['baseline_score']).sum()}")
	print(f"Baseline better than alternative: {(basil_reg_df['alternative_score'] < basil_reg_df['baseline_score']).sum()}")

	print("PRS-CS regression:")
	print(f"Alternative better than baseline: {(prscs_reg_df['alternative_score'] > prscs_reg_df['baseline_score']).sum()}")
	print(f"Baseline better than alternative: {(prscs_reg_df['alternative_score'] < prscs_reg_df['baseline_score']).sum()}")


