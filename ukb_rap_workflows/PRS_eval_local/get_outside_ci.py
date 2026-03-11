"""Find pairwise scores outside the upper CI of the baseline approach."""

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
	'age_sex_all_coords_time_pc_null_xgb_3_bin_cls_age_sex_all_coords_time_pc': 'age, sex, locations, times, PCs for null',
}

MODEL_CONFIGS = [
	{
		'label': 'BASIL classification',
		'model_type': 'BASIL',
		'metric': 'average_precision',
	},
	{
		'label': 'BASIL regression',
		'model_type': 'BASIL',
		'metric': 'r2',
	},
	{
		'label': 'PRS-CS regression',
		'model_type': 'PRScs',
		'metric': 'r2',
	},
]


if __name__ == "__main__":

	scores_df = pd.read_csv('sup_table/sup_table_results_long.csv')

	for config in MODEL_CONFIGS:
		print(f"\n{'='*60}")
		print(f"{config['label']}")
		print(f"{'='*60}")

		model_scores = scores_df[
			(scores_df['model_type'] == config['model_type'])
			& (scores_df['metric'] == config['metric'])
		]

		for pheno in sorted(model_scores['pheno'].unique()):
			# Get baseline upper CI
			baseline = model_scores[
				(model_scores['pheno'] == pheno)
				& (model_scores['covar_set'] == 'age, sex')
				& (model_scores['uses_null'] == False)
			]

			if len(baseline) != 1:
				print(f"  WARNING: Expected 1 baseline for {pheno}, got {len(baseline)}")
				continue

			baseline_upper = baseline['upper'].item()
			baseline_value = baseline['value'].item()

			# Check all alternative covariate sets
			alternatives = model_scores[
				(model_scores['pheno'] == pheno)
				& ~(
					(model_scores['covar_set'] == 'age, sex')
					& (model_scores['uses_null'] == False)
				)
			]

			outside = alternatives[alternatives['value'] > baseline_upper]

			if len(outside) > 0:
				print(f"\n  {pheno} (baseline {config['metric']}={baseline_value:.4f}, upper CI={baseline_upper:.4f}):")
				for _, row in outside.iterrows():
					null_str = " (null model)" if row['uses_null'] else ""
					print(
						f"    covars=[{row['covar_set']}]{null_str}: "
						f"{config['metric']}={row['value']:.4f}"
					)