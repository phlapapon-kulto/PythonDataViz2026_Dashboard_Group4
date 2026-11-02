import unittest
import os
import pandas as pd
import numpy as np
import scipy.stats as stats

class TestAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.processed_dir = os.path.join(cls.repo_dir, "data", "processed")
        cls.df_panel = pd.read_csv(os.path.join(cls.processed_dir, "weekly_panel_final.csv"))

    def test_pearson_correlation_all_48_weeks(self):
        """Test Pearson correlation across all 48 reported weeks"""
        reported = self.df_panel[self.df_panel['acsc_reported'] == True]
        r_cases, p_cases = stats.pearsonr(reported['afnc_false_finance'], reported['acsc_cases'])
        r_loss, p_loss = stats.pearsonr(reported['afnc_false_finance'], reported['acsc_loss_baht'])

        self.assertAlmostEqual(r_cases, -0.0903, places=3)
        self.assertAlmostEqual(p_cases, 0.5418, places=3)
        self.assertAlmostEqual(r_loss, 0.0557, places=3)
        self.assertAlmostEqual(p_loss, 0.7070, places=3)

    def test_pearson_correlation_excluding_outlier(self):
        """Test Pearson correlation for 47 weeks excluding flagged outlier week 2026-08-16"""
        reported = self.df_panel[self.df_panel['acsc_reported'] == True]
        clean_weeks = reported[reported['week_start'] != '2026-08-16']
        self.assertEqual(len(clean_weeks), 47)

        r_cases, p_cases = stats.pearsonr(clean_weeks['afnc_false_finance'], clean_weeks['acsc_cases'])
        r_loss, p_loss = stats.pearsonr(clean_weeks['afnc_false_finance'], clean_weeks['acsc_loss_baht'])

        self.assertAlmostEqual(r_cases, 0.5377, places=3)
        self.assertTrue(p_cases < 0.001)
        self.assertAlmostEqual(r_loss, 0.5720, places=3)
        self.assertTrue(p_loss < 0.0001)

    def test_average_loss_per_case(self):
        """Test average loss per case calculation"""
        reported = self.df_panel[self.df_panel['acsc_reported'] == True]
        total_loss = reported['acsc_loss_baht'].sum()
        total_cases = reported['acsc_cases'].sum()
        avg_loss_per_case = total_loss / total_cases

        # Total reported loss: 18,177,372,691 THB; Total cases: 381,390 cases
        self.assertAlmostEqual(avg_loss_per_case, 47660.85, places=1)

if __name__ == '__main__':
    unittest.main()
