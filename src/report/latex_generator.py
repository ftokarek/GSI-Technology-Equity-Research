
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
        
    def generate_latex_table(self, df: pd.DataFrame, caption: str, label: str, scale: float = 0.9) -> str:
        
        num_cols = len(df.columns)
        col_format = 'l' + 'r' * (num_cols - 1)
        
        latex = f"\n\\begin{{table}}[H]\n"
        latex += f"\\centering\n"
        latex += f"\\caption{{{caption}}}\n"
        latex += f"\\label{{{label}}}\n"
        latex += f"\\scalebox{{{scale}}}{{\n"
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
                    if abs(val) < 1:
                        row_data.append(f"{val:.3f}")
                    else:
                        row_data.append(f"{val:,.1f}")
                else:
                    row_data.append(str(val).replace('_', ' '))
            
            latex += " & ".join(row_data) + " \\\\\n"
        
        latex += "\\bottomrule\n"
        latex += "\\end{tabular}\n"
        latex += "}\n"
        latex += "\\end{table}\n\n"
        
        return latex
    
    def generate_executive_summary_section(self) -> str:
        rec = self.final_rec.iloc[0]
        
        latex = "\\section{Executive Summary}\n\n"
        latex += "\\vspace{0.5cm}\n\n"
        
        latex += "\\begin{center}\n"
        latex += "\\begin{tabular}{ll}\n"
        latex += "\\toprule\n"
        latex += "\\textbf{Company} & GSI Technology Inc. (NASDAQ: GSIT) \\\\\n"
        latex += f"\\textbf{{Analyst}} & Franciszek Tokarek \\\\\n"
        latex += f"\\textbf{{Analysis Date}} & {self.executive_summary.iloc[0]['analysis_date']} \\\\\n"
        latex += f"\\textbf{{Recommendation}} & \\textcolor{{red}}{{\\textbf{{{rec['recommendation']}}}}} \\\\\n"
        latex += f"\\textbf{{Confidence}} & {rec['confidence']} \\\\\n"
        latex += f"\\textbf{{Score}} & {rec['score']}/10 \\\\\n"
        latex += "\\bottomrule\n"
        latex += "\\end{tabular}\n"
        latex += "\\end{center}\n\n"
        latex += "\\vspace{0.5cm}\n\n"
        
        latex += "\\subsection{Key Findings}\n\n"
        latex += "\\begin{itemize}\n"
        latex += "\\itemsep0.3em\n"
        latex += f"\\item Revenue declining at {self.growth_metrics.tail(1)['revenue_cagr_3y'].iloc[0]:.1f}\\% 3-year CAGR\n"
        latex += f"\\item Gross margins remain strong at {self.profitability.tail(3)['gross_margin'].mean():.1f}\\%\n"
        latex += f"\\item Operating margins negative at {self.profitability.tail(3)['operating_margin'].mean():.1f}\\%\n"
        latex += f"\\item Cash position critical at \\${self.balance_metrics.iloc[-1]['cash']:,.0f}K with 12-month runway\n"
        latex += f"\\item Stock-based compensation high at 14.8\\% of revenue\n"
        latex += "\\end{itemize}\n\n"
        latex += "\\vspace{0.3cm}\n\n"
        
        latex += "\\subsection{Investment Suitability}\n\n"
        latex += f"\\noindent {rec['suitable_for']}\n\n"
        
        latex += "\\vspace{0.3cm}\n\n"
        latex += "\\subsection{Risk Tolerance Required}\n\n"
        latex += f"\\noindent \\textbf{{Risk Level:}} {rec['risk_tolerance']}\n\n"
        
        return latex
    
    def generate_financial_performance_section(self) -> str:
        latex = "\\section{Financial Performance Analysis}\n\n"
        
        latex += "\\subsection{Revenue Analysis}\n\n"
        latex += "GSI Technology has experienced significant revenue decline over the analysis period. "
        latex += f"The most recent fiscal year (2025) reported revenue of \\${self.growth_metrics.iloc[-1]['revenue']:,.0f}K, "
        latex += f"representing a {self.growth_metrics.iloc[-1]['revenue_cagr_3y']:.1f}\\% 3-year CAGR.\n\n"
        
        recent_growth = self.growth_metrics.tail(8)
        latex += self.generate_latex_table(
            recent_growth[['year', 'revenue', 'revenue_growth_yoy', 'revenue_cagr_3y']],
            "Revenue Growth Metrics (Recent 8 Years)",
            "tab:revenue_growth",
            scale=0.95
        )
        
        latex += "\\subsection{Profitability Analysis}\n\n"
        latex += f"Gross margins have remained relatively strong, averaging {self.profitability.tail(5)['gross_margin'].mean():.1f}\\% "
        latex += f"over the past 5 years. However, operating margins are deeply negative at {self.profitability.tail(3)['operating_margin'].mean():.1f}\\% "
        latex += "due to high operating expenses relative to revenue.\n\n"
        
        recent_profit = self.profitability.tail(8)
        latex += self.generate_latex_table(
            recent_profit[['year', 'revenue', 'gross_margin', 'operating_margin', 'net_margin']],
            "Profitability Margins (Recent 8 Years)",
            "tab:profitability",
            scale=0.95
        )
        
        latex += "\\subsection{Balance Sheet Strength}\n\n"
        latex += f"The company maintains good liquidity with a current ratio of {self.balance_metrics.iloc[-1]['current_ratio']:.2f}, "
        latex += f"though cash has declined significantly to \\${self.balance_metrics.iloc[-1]['cash']:,.0f}K, "
        latex += "providing approximately 12 months of runway at current burn rates.\n\n"
        
        recent_balance = self.balance_metrics.tail(8)
        balance_subset = recent_balance[['year', 'cash', 'total_assets', 'current_ratio']].copy()
        latex += self.generate_latex_table(
            balance_subset,
            "Balance Sheet Metrics (Recent 8 Years)",
            "tab:balance_sheet",
            scale=1.0
        )
        
        return latex
    
    def generate_scenario_analysis_section(self) -> str:
        latex = "\\section{Scenario Analysis}\n\n"
        
        latex += "Three scenarios have been modeled to assess potential five-year outcomes "
        latex += "based on different assumptions about operational performance and market conditions.\n\n"
        latex += "\\vspace{0.3cm}\n\n"
        
        latex += self.generate_latex_table(
            self.scenarios,
            "Investment Scenarios - Bull/Base/Bear Analysis",
            "tab:scenarios",
            scale=0.85
        )
        
        latex += "\\vspace{0.3cm}\n\n"
        latex += "\\subsection{Scenario Implications}\n\n"
        
        for _, scenario in self.scenarios.iterrows():
            scenario_name = scenario['name'].replace('_', ' ')
            latex += f"\\textbf{{{scenario_name}}} ({scenario['probability']:.0f}\\% probability)\n\n"
            latex += "\\begin{itemize}\n"
            latex += "\\itemsep0.2em\n"
            latex += f"\\item 5-Year Revenue: \\${scenario['five_year_revenue']:,.0f}K\n"
            latex += f"\\item Revenue CAGR: {scenario['five_year_cagr']:.1f}\\%\n"
            latex += f"\\item Implied Enterprise Value: \\${scenario['implied_enterprise_value']:,.0f}K\n"
            latex += "\\end{itemize}\n\n"
            latex += "\\vspace{0.2cm}\n\n"
        
        return latex
    
    def generate_recommendation_section(self) -> str:
        rec = self.final_rec.iloc[0]
        
        latex = "\\section{Investment Recommendation}\n\n"
        
        latex += f"\\subsection{{Primary Recommendation: \\textcolor{{red}}{{{rec['recommendation']}}}}}\n\n"
        latex += f"Based on comprehensive analysis of financial performance, market position, and future scenarios, "
        latex += f"the recommendation is to \\textbf{{{rec['recommendation']}}} GSI Technology stock.\n\n"
        latex += "\\vspace{0.3cm}\n\n"
        
        latex += "\\subsection{Recommendation by Investment Horizon}\n\n"
        latex += "\\begin{itemize}\n"
        latex += "\\itemsep0.3em\n"
        latex += f"\\item \\textbf{{Short-term (1-2 years):}} {rec['short_term_rec']} - Cash runway concerns require immediate attention\n"
        latex += f"\\item \\textbf{{Medium-term (3-5 years):}} {rec['medium_term_rec']} - Wait for revenue stabilization signals\n"
        latex += f"\\item \\textbf{{Long-term (5+ years):}} {rec['long_term_rec']} - Strategic value may attract acquirer\n"
        latex += "\\end{itemize}\n\n"
        latex += "\\vspace{0.3cm}\n\n"
        
        latex += "\\subsection{Key Risk Factors}\n\n"
        latex += "\\begin{enumerate}\n"
        latex += "\\itemsep0.3em\n"
        latex += "\\item \\textbf{Revenue Decline:} 53\\% decline over 5 years with -15\\% 3-year CAGR\n"
        latex += "\\item \\textbf{Operating Losses:} Persistent negative operating margins averaging -73\\%\n"
        latex += "\\item \\textbf{Cash Position:} Critical cash level of \\$1M providing only 12-month runway\n"
        latex += "\\item \\textbf{Market Share:} Declining competitive position in niche SRAM market (<1\\% share)\n"
        latex += "\\item \\textbf{Dilution:} High stock-based compensation at 14.8\\% of revenue\n"
        latex += "\\end{enumerate}\n\n"
        latex += "\\vspace{0.3cm}\n\n"
        
        latex += "\\subsection{Potential Opportunities}\n\n"
        latex += "\\begin{enumerate}\n"
        latex += "\\itemsep0.3em\n"
        latex += "\\item \\textbf{Strong Gross Margins:} 64\\% average demonstrates product differentiation\n"
        latex += "\\item \\textbf{Acquisition Target:} Low valuation and IP portfolio may attract strategic buyers\n"
        latex += "\\item \\textbf{APU Technology:} Potential applications in AI/ML in-memory computing\n"
        latex += "\\item \\textbf{Operational Turnaround:} Cost cutting and revenue stabilization possible\n"
        latex += "\\item \\textbf{Valuation:} Trading below book value with 1,536\\% upside in bull scenario\n"
        latex += "\\end{enumerate}\n\n"
        latex += "\\vspace{0.3cm}\n\n"
        
        latex += "\\subsection{Conclusion}\n\n"
        latex += f"\\noindent {rec['suitable_for']} The current financial trajectory presents "
        latex += "significant challenges, but the company's technology assets and potential for strategic "
        latex += "acquisition provide speculative upside for investors with very high risk tolerance.\n\n"
        
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
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{fancyhdr}
\onehalfspacing

\definecolor{darkblue}{RGB}{0,51,102}
\titleformat{\section}{\Large\bfseries\color{darkblue}}{\thesection}{1em}{}
\titleformat{\subsection}{\large\bfseries}{\thesubsection}{1em}{}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{GSI Technology - Equity Research}
\fancyhead[R]{Franciszek Tokarek}
\fancyfoot[C]{\thepage}

\title{\Huge\bfseries GSI Technology Inc. \\ \Large Comprehensive Equity Research Report}
\author{\Large Franciszek Tokarek \\ \normalsize Independent Equity Analysis}
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

