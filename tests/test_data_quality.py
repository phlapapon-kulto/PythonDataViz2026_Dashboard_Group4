import unittest
import os
import pandas as pd
import numpy as np
import scipy.stats as stats

class TestDataQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.processed_dir = os.path.join(cls.repo_dir, "data", "processed")
        
        cls.df_aiid = pd.read_csv(os.path.join(cls.processed_dir, "ai_incidents_clean.csv"))
        cls.df_afnc = pd.read_csv(os.path.join(cls.processed_dir, "afnc_items_clean.csv"))
        cls.df_acsc = pd.read_csv(os.path.join(cls.processed_dir, "acsc_weekly_clean.csv"))
        cls.df_panel = pd.read_csv(os.path.join(cls.processed_dir, "weekly_panel_final.csv"))

    def test_aiid_primary_key_uniqueness(self):
        """Test that AIID Incident ID is 100% unique and non-null"""
        self.assertEqual(len(self.df_aiid), 1749)
        self.assertEqual(self.df_aiid['incident_id'].nunique(), 1749)
        self.assertEqual(self.df_aiid['incident_id'].isnull().sum(), 0)

    def test_aiid_casualties_calculation(self):
        """Test that confirmed casualties count is strictly 21 incidents"""
        confirmed = ((self.df_aiid['injuries'] > 0) | (self.df_aiid['lives_lost'] > 0)).sum()
        self.assertEqual(confirmed, 21)
        self.assertEqual(self.df_aiid['has_casualties'].sum(), 21)

    def test_afnc_post_id_uniqueness(self):
        """Test that AFNC post_id is 100% unique and non-null"""
        self.assertEqual(len(self.df_afnc), 17726)
        self.assertEqual(self.df_afnc['post_id'].nunique(), 17726)
        self.assertEqual(self.df_afnc['post_id'].isnull().sum(), 0)

    def test_afnc_financial_news_counts(self):
        """Test primary financial news count and verdict percentages"""
        fin = self.df_afnc[self.df_afnc['category_th'] == 'การเงิน-หุ้น']
        self.assertEqual(len(fin), 2514)
        
        fake_fin = fin[fin['verdict_th'] == 'ข่าวปลอม']
        self.assertEqual(len(fake_fin), 2339)
        
        pct = (len(fake_fin) / len(fin)) * 100
        self.assertAlmostEqual(pct, 93.0389, places=2)

    def test_weekly_panel_integration(self):
        """Test that weekly panel has 409 continuous Sunday weeks and 48 reported weeks"""
        self.assertEqual(len(self.df_panel), 409)
        self.assertEqual(self.df_panel['week_start'].nunique(), 409)
        reported = self.df_panel[self.df_panel['acsc_reported'] == True]
        self.assertEqual(len(reported), 48)

    def test_missing_values_preserved_not_zero(self):
        """Test that unreported acsc_cases prior to briefing start are preserved as NaN, not zero"""
        unreported = self.df_panel[self.df_panel['acsc_reported'] == False]
        self.assertTrue(unreported['acsc_cases'].isna().all())
        self.assertTrue(unreported['acsc_loss_baht'].isna().all())

    def test_view_counts_non_negative(self):
        """Test that view counts in AFNC are strictly positive integers"""
        self.assertTrue((self.df_afnc['view_count'] > 0).all())
        self.assertEqual(self.df_afnc['view_count'].isna().sum(), 0)

if __name__ == '__main__':
    unittest.main()
