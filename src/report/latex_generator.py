
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

class LaTeXReportGenerator:
    
    def __init__(self, analysis_dir: str = "data/analysis"):
        self.analysis_dir = Path(analysis_dir)
        self.load_analysis_results()
        
    def load_analysis_results(self):
        print("Loading analysis results for LaTeX report...")
        
        self.executive_summary = pd.read_csv(self.analysis_dir / "executive_summary.csv")
        self.growth_metrics = pd.read_csv(self.analysis_dir / "complete_growth_metrics.csv")
        self.profitability = pd.read_csv(self.analysis_dir / "complete_profitability_metrics.csv")
        self.balance_metrics = pd.read_csv(self.analysis_dir / "complete_balance_sheet_metrics.csv")
        self.returns = pd.read_csv(self.analysis_dir / "complete_returns_metrics.csv")
        self.scenarios = pd.read_csv(self.analysis_dir / "scenario_analysis_summary.csv")
        self.final_rec = pd.read_csv(self.analysis_dir / "complete_investment_decision.csv")
        
        print(f"Loaded {7} analysis files")
        
    def generate_latex_table(self, df: pd.DataFrame, caption: str, label: str) -> str:
        
        num_cols = len(df.columns)
        col_format = 'l' + 'r' * (num_cols - 1)
        
        latex = f"\\begin{{table}}[htbp]\n"
        latex += f"\\centering\n"
        latex += f"\\caption{{{caption}}}\n"
        latex += f"\\label{{{label}}}\n"
        latex += f"\\begin{{tabular}}{{{col_format}}}\n"
        latex += "\\toprule\n"
        
        headers = " & ".join([str(col).replace('_', ' ').title() for col in df.columns])
        latex += f"{headers} \\\\\n"
        latex += "\\midrule\n"
        
        for _, row in df.iterrows():
            row_data = []
            for val in row:
                if pd.isna(val):
                    row_data.append("--")
                elif isinstance(val, (int, np.integer)):
                    row_data.append(f"{val:,}")
                elif isinstance(val, (float, np.floating)):
                    row_data.append(f"{val:,.2f}")
                else:
                    row_data.append(str(val))
            
            latex += " & ".join(row_data) + " \\\\\n"
        
        latex += "\\bottomrule\n"
        latex += "\\end{tabular}\n"
        latex += "\\end{table}\n"
        
        return latex
    
    def generate_executive_summary_section(self) -> str:
        rec = self.final_rec.iloc[0]
        
        latex = "\\section{Executive Summary}\n\n"
        
        latex += f"\\textbf{{Company:}} GSI Technology Inc. (NASDAQ: GSIT)\n\n"
        latex += f"\\textbf{{Analysis Date:}} {self.executive_summary.iloc[0]['analysis_date']}\n\n"
        latex += f"\\textbf{{Investment Recommendation:}} {rec['recommendation']}\n\n"
        latex += f"\\textbf{{Confidence Level:}} {rec['confidence']}\n\n"
        latex += f"\\textbf{{Investment Score:}} {rec['score']}/10\n\n"
        
        latex += "\\subsection{Key Findings}\n\n"
        latex += "\\begin{itemize}\n"
        latex += f"\\item Revenue declining at {self.growth_metrics.tail(1)['revenue_cagr_3y'].iloc[0]:.1f}\\% 3-year CAGR\n"
        latex += f"\\item Gross margins remain strong at {self.profitability.tail(3)['gross_margin'].mean():.1f}\\%\n"
        latex += f"\\item Operating margins negative at {self.profitability.tail(3)['operating_margin'].mean():.1f}\\%\n"
        latex += f"\\item Cash position critical at \\${self.balance_metrics.iloc[-1]['cash']:,.0f}K\n"
        latex += "\\end{itemize}\n\n"
        
        latex += "\\subsection{Investment Suitability}\n\n"
        latex += f"{rec['suitable_for']}\n\n"
        
        return latex
    
    def generate_financial_performance_section(self) -> str:
        latex = "\\section{Financial Performance Analysis}\n\n"
        
        latex += "\\subsection{Revenue Analysis}\n\n"
        
        recent_growth = self.growth_metrics.tail(10)
        latex += self.generate_latex_table(
            recent_growth[['year', 'revenue', 'revenue_growth_yoy', 'revenue_cagr_3y']],
            "Revenue Growth Metrics (10-Year)",
            "tab:revenue_growth"
        )
        
        latex += "\n\\subsection{Profitability Analysis}\n\n"
        
        recent_profit = self.profitability.tail(10)
        latex += self.generate_latex_table(
            recent_profit[['year', 'revenue', 'gross_margin', 'operating_margin', 'net_margin']],
            "Profitability Margins (10-Year)",
            "tab:profitability"
        )
        
        latex += "\n\\subsection{Balance Sheet Strength}\n\n"
        
        recent_balance = self.balance_metrics.tail(10)
        latex += self.generate_latex_table(
            recent_balance[['year', 'cash', 'total_assets', 'current_ratio', 'debt_to_equity']],
            "Balance Sheet Metrics (10-Year)",
            "tab:balance_sheet"
        )
        
        return latex
    
    def generate_scenario_analysis_section(self) -> str:
        latex = "\\section{Scenario Analysis}\n\n"
        
        latex += "Three scenarios have been modeled to assess potential outcomes:\n\n"
        
        latex += self.generate_latex_table(
            self.scenarios,
            "Investment Scenarios - Bull/Base/Bear Analysis",
            "tab:scenarios"
        )
        
        latex += "\n\\subsection{Scenario Implications}\n\n"
        latex += "\\begin{description}\n"
        
        for _, scenario in self.scenarios.iterrows():
            latex += f"\\item[{scenario['name']}] ({scenario['probability']}\\% probability)\n"
            latex += f"5-Year Revenue: \\${scenario['five_year_revenue']:,.0f}K, "
            latex += f"CAGR: {scenario['five_year_cagr']:.1f}\\%, "
            latex += f"Valuation: \\${scenario['implied_enterprise_value']:,.0f}K\n\n"
        
        latex += "\\end{description}\n\n"
        
        return latex
    
    def generate_recommendation_section(self) -> str:
        rec = self.final_rec.iloc[0]
        
        latex = "\\section{Investment Recommendation}\n\n"
        
        latex += f"\\subsection{{Primary Recommendation: {rec['recommendation']}}}\n\n"
        
        latex += "\\subsubsection{Recommendation by Time Horizon}\n\n"
        latex += "\\begin{itemize}\n"
        latex += f"\\item \\textbf{{Short-term (1-2 years):}} {rec['short_term_rec']}\n"
        latex += f"\\item \\textbf{{Medium-term (3-5 years):}} {rec['medium_term_rec']}\n"
        latex += f"\\item \\textbf{{Long-term (5+ years):}} {rec['long_term_rec']}\n"
        latex += "\\end{itemize}\n\n"
        
        latex += "\\subsection{Risk Factors}\n\n"
        latex += "\\begin{itemize}\n"
        latex += "\\item Revenue decline: -53\\% over 5 years\n"
        latex += "\\item Negative operating margins averaging -73\\%\n"
        latex += "\\item Critical cash position of \\$1M with 12-month runway\n"
        latex += "\\item High stock-based compensation (14.8\\% of revenue)\n"
        latex += "\\end{itemize}\n\n"
        
        latex += "\\subsection{Investment Opportunities}\n\n"
        latex += "\\begin{itemize}\n"
        latex += "\\item Strong gross margins (64\\% average)\n"
        latex += "\\item Potential acquisition target\n"
        latex += "\\item APU technology AI/ML applications\n"
        latex += "\\item Undervalued based on book value\n"
        latex += "\\end{itemize}\n\n"
        
        return latex
    
    def generate_full_report(self, output_file: str = "output/equity_research_report.tex"):
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        latex = self.generate_latex_header()
        latex += "\n\\begin{document}\n\n"
        latex += self.generate_title_page()
        latex += "\n\\tableofcontents\n"
        latex += "\n\\newpage\n\n"
        latex += self.generate_executive_summary_section()
        latex += "\n\\newpage\n\n"
        latex += self.generate_financial_performance_section()
        latex += "\n\\newpage\n\n"
        latex += self.generate_scenario_analysis_section()
        latex += "\n\\newpage\n\n"
        latex += self.generate_recommendation_section()
        latex += "\n\\end{document}\n"
        
        with open(output_path, 'w') as f:
            f.write(latex)
        
        print(f"LaTeX report generated: {output_path}")
        
        return str(output_path)
    
    def generate_latex_header(self) -> str:
        return r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[english]{babel}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{float}
\usepackage{setspace}
\onehalfspacing

\title{GSI Technology Inc. \\ Equity Research Report}
\author{Independent Analysis}
\date{\today}
"""
    
    def generate_title_page(self) -> str:
        return r"""
\maketitle
\thispagestyle{empty}

\begin{abstract}
This report presents a comprehensive equity analysis of GSI Technology Inc. (NASDAQ: GSIT), 
covering financial performance from 2011 to 2025. The analysis includes trend analysis, 
valuation assessment, scenario modeling, and strategic evaluation to provide an informed 
investment recommendation.
\end{abstract}

\newpage
"""

def main():
    generator = LaTeXReportGenerator()
    output_file = generator.generate_full_report()
    print(f"\nLaTeX report ready: {output_file}")
    print("Run: pdflatex output/equity_research_report.tex")
    
if __name__ == "__main__":
    main()

