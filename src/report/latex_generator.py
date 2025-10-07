
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
        
    def format_value_for_latex(self, val, col_name: str) -> str:
        if pd.isna(val):
            return "--"
        
        col_lower = col_name.lower()
        
        if col_lower == 'year':
            return f"{int(val)}"
        
        if isinstance(val, (int, np.integer)):
            if 'year' in col_lower:
                return f"{val}"
            return f"{val:,}"
        
        if isinstance(val, (float, np.floating)):
            if 'margin' in col_lower or 'growth' in col_lower or 'cagr' in col_lower or 'roe' in col_lower or 'roa' in col_lower or 'roic' in col_lower or 'return' in col_lower:
                return f"{val:.1f}\\%"
            elif 'ratio' in col_lower or 'turnover' in col_lower:
                return f"{val:.2f}"
            elif col_lower in ['revenue', 'cash', 'ebit', 'ebitda', 'net_income', 'gross_profit'] or 'assets' in col_lower or 'debt' in col_lower or 'equity' in col_lower:
                if abs(val) >= 1:
                    return f"\\${val/1000:.1f}M"
                else:
                    return f"\\${val:.3f}M"
            else:
                if abs(val) < 1:
                    return f"{val:.3f}"
                else:
                    return f"{val:,.1f}"
        
        return str(val).replace('_', ' ')
    
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
            for col_name, val in row.items():
                row_data.append(self.format_value_for_latex(val, col_name))
            
            latex += " & ".join(row_data) + " \\\\\n"
        
        latex += "\\bottomrule\n"
        latex += "\\end{tabular}\n"
        latex += "}\n"
        latex += "\\end{table}\n\n"
        
        return latex
    
    def generate_executive_summary_section(self) -> str:
        rec = self.final_rec.iloc[0]
        
        latex = "\\section{Executive Summary}\n\n"
        
        latex += "\\begin{center}\n"
        latex += "\\fcolorbox{darkblue}{lightgray}{\n"
        latex += "\\begin{minipage}{0.9\\textwidth}\n"
        latex += "\\vspace{0.3cm}\n"
        latex += "\\centering\n"
        latex += "\\begin{tabular}{ll}\n"
        latex += "\\textbf{Company} & GSI Technology Inc. (NASDAQ: GSIT) \\\\\n"
        latex += f"\\textbf{{Analyst}} & Franciszek Tokarek \\\\\n"
        latex += f"\\textbf{{Report Date}} & {self.executive_summary.iloc[0]['analysis_date']} \\\\\n"
        latex += "\\midrule\n"
        latex += f"\\textbf{{Recommendation}} & \\textcolor{{darkred}}{{\\Large\\textbf{{{rec['recommendation']}}}}} \\\\\n"
        latex += f"\\textbf{{Confidence Level}} & {rec['confidence']} \\\\\n"
        latex += f"\\textbf{{Investment Score}} & {rec['score']}/10 \\\\\n"
        latex += "\\end{tabular}\n"
        latex += "\\vspace{0.3cm}\n"
        latex += "\\end{minipage}\n"
        latex += "}\n"
        latex += "\\end{center}\n\n"
        latex += "\\vspace{0.8cm}\n\n"
        
        latex += "\\subsection{Key Findings}\n\n"
        latex += "\\begin{itemize}\n"
        latex += "\\setlength{\\itemsep}{0.4em}\n"
        latex += f"\\item \\textbf{{Revenue Trend:}} Declining at {self.growth_metrics.tail(1)['revenue_cagr_3y'].iloc[0]:.1f}\\% 3-year CAGR (from \\$33.4M in 2023 to \\$20.5M in 2025)\n"
        latex += f"\\item \\textbf{{Gross Margins:}} Strong at {self.profitability.tail(3)['gross_margin'].mean():.1f}\\% average, demonstrating pricing power\n"
        latex += f"\\item \\textbf{{Operating Margins:}} Deeply negative at {self.profitability.tail(3)['operating_margin'].mean():.1f}\\%, indicating operational challenges\n"
        latex += f"\\item \\textbf{{Cash Position:}} Critical level of \\${self.balance_metrics.iloc[-1]['cash']/1000:.1f}M providing approximately 12-month runway\n"
        latex += f"\\item \\textbf{{Liquidity:}} Current ratio of {self.balance_metrics.iloc[-1]['current_ratio']:.2f} indicates adequate short-term liquidity\n"
        latex += "\\end{itemize}\n\n"
        latex += "\\vspace{0.5cm}\n\n"
        
        latex += "\\subsection{Investment Suitability}\n\n"
        latex += "\\begin{quote}\n"
        latex += f"\\textit{{{rec['suitable_for']}}} This investment requires \\textbf{{{rec['risk_tolerance']}}} risk tolerance "
        latex += "and is not suitable for conservative or income-focused investors.\n"
        latex += "\\end{quote}\n\n"
        
        return latex
    
    def generate_financial_performance_section(self) -> str:
        latex = "\\section{Financial Performance Analysis}\n\n"
        
        latex += "\\subsection{Revenue Analysis}\n\n"
        latex += "GSI Technology has experienced significant revenue decline over the analysis period. "
        latex += f"The most recent fiscal year (2025) reported revenue of \\${self.growth_metrics.iloc[-1]['revenue']/1000:.1f}M, "
        latex += f"representing a {self.growth_metrics.iloc[-1]['revenue_cagr_3y']:.1f}\\% 3-year CAGR.\n\n"
        
        recent_growth = self.growth_metrics.tail(8)
        latex += "\\small{\\textit{Note: Revenue figures in millions (\\$M), growth rates and CAGR in percentages.}}\n\n"
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
        latex += "\\small{\\textit{Note: Revenue in millions (\\$M), margins in percentages (\\%).}}\n\n"
        latex += self.generate_latex_table(
            recent_profit[['year', 'revenue', 'gross_margin', 'operating_margin', 'net_margin']],
            "Profitability Margins (Recent 8 Years)",
            "tab:profitability",
            scale=0.95
        )
        
        latex += "\\subsection{Balance Sheet Strength}\n\n"
        latex += f"The company maintains good liquidity with a current ratio of {self.balance_metrics.iloc[-1]['current_ratio']:.2f}, "
        latex += f"though cash has declined significantly to \\${self.balance_metrics.iloc[-1]['cash']/1000:.1f}M, "
        latex += "providing approximately 12 months of runway at current burn rates.\n\n"
        
        recent_balance = self.balance_metrics.tail(8)
        balance_subset = recent_balance[['year', 'cash', 'total_assets', 'current_ratio']].copy()
        latex += "\\small{\\textit{Note: Cash and assets in millions (\\$M), ratios are unitless.}}\n\n"
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
            latex += f"\\item 5-Year Revenue: \\${scenario['five_year_revenue']/1000:.1f}M\n"
            latex += f"\\item Revenue CAGR: {scenario['five_year_cagr']:.1f}\\%\n"
            latex += f"\\item Implied Enterprise Value: \\${scenario['implied_enterprise_value']/1000:.1f}M\n"
            latex += "\\end{itemize}\n\n"
            latex += "\\vspace{0.2cm}\n\n"
        
        return latex
    
    def generate_recommendation_section(self) -> str:
        rec = self.final_rec.iloc[0]
        
        latex = "\\section{Investment Recommendation}\n\n"
        
        latex += "\\begin{center}\n"
        latex += "\\fcolorbox{darkred}{white}{\n"
        latex += "\\begin{minipage}{0.85\\textwidth}\n"
        latex += "\\vspace{0.3cm}\n"
        latex += "\\centering\n"
        latex += f"{{\\Huge\\textcolor{{darkred}}{{\\textbf{{{rec['recommendation']}}}}}}}\\\\[0.3cm]\n"
        latex += f"{{\\large Confidence: {rec['confidence']} | Score: {rec['score']}/10}}\n"
        latex += "\\vspace{0.3cm}\n"
        latex += "\\end{minipage}\n"
        latex += "}\n"
        latex += "\\end{center}\n\n"
        latex += "\\vspace{0.5cm}\n\n"
        
        latex += f"Based on comprehensive analysis of financial performance, market position, and future scenarios, "
        latex += f"the recommendation is to \\textbf{{{rec['recommendation']}}} GSI Technology stock.\n\n"
        latex += "\\vspace{0.5cm}\n\n"
        
        latex += "\\subsection{Recommendation by Investment Horizon}\n\n"
        latex += "\\begin{center}\n"
        latex += "\\begin{tabular}{p{3cm}p{10cm}}\n"
        latex += "\\toprule\n"
        latex += "\\textbf{Horizon} & \\textbf{Recommendation} \\\\\n"
        latex += "\\midrule\n"
        latex += f"Short-term\\newline(1-2 years) & \\textbf{{{rec['short_term_rec']}}} -- Cash runway concerns require immediate monitoring. Liquidity position remains adequate but declining. \\\\\n"
        latex += f"Medium-term\\newline(3-5 years) & \\textbf{{{rec['medium_term_rec']}}} -- Revenue stabilization signals needed before considering entry. Operational turnaround remains uncertain. \\\\\n"
        latex += f"Long-term\\newline(5+ years) & \\textbf{{{rec['long_term_rec']}}} -- Strategic value and IP portfolio may attract acquisition interest from larger players. \\\\\n"
        latex += "\\bottomrule\n"
        latex += "\\end{tabular}\n"
        latex += "\\end{center}\n\n"
        latex += "\\vspace{0.5cm}\n\n"
        
        latex += "\\subsection{Risk Assessment}\n\n"
        latex += "\\subsubsection{Primary Risk Factors}\n\n"
        latex += "\\begin{enumerate}\n"
        latex += "\\setlength{\\itemsep}{0.4em}\n"
        latex += "\\item \\textbf{Revenue Decline:} 53\\% decline over 5 years with -15\\% 3-year CAGR, indicating persistent market share losses\n"
        latex += "\\item \\textbf{Operating Losses:} Negative operating margins averaging -73\\%, with no clear path to profitability\n"
        latex += f"\\item \\textbf{{Cash Burn:}} Critical cash level of \\${self.balance_metrics.iloc[-1]['cash']/1000:.1f}M provides only 12-month runway at current burn rate\n"
        latex += "\\item \\textbf{Market Position:} Less than 1\\% market share in niche SRAM market, vulnerable to larger competitors\n"
        latex += "\\item \\textbf{Dilution Risk:} Stock-based compensation at 14.8\\% of revenue creates shareholder dilution concerns\n"
        latex += "\\end{enumerate}\n\n"
        latex += "\\vspace{0.5cm}\n\n"
        
        latex += "\\subsubsection{Potential Upside Opportunities}\n\n"
        latex += "\\begin{enumerate}\n"
        latex += "\\setlength{\\itemsep}{0.4em}\n"
        latex += f"\\item \\textbf{{Product Differentiation:}} {self.profitability.tail(3)['gross_margin'].mean():.1f}\\% average gross margin demonstrates strong pricing power\n"
        latex += "\\item \\textbf{Acquisition Value:} Low enterprise valuation combined with valuable IP portfolio makes company attractive acquisition target\n"
        latex += "\\item \\textbf{Technology Platform:} APU (Associative Processing Unit) technology has potential applications in AI/ML space\n"
        latex += "\\item \\textbf{Turnaround Potential:} Operational improvements could restore profitability if revenue stabilizes\n"
        latex += "\\item \\textbf{Valuation Upside:} Currently trading significantly below historical valuations with 1,536\\% upside in bull scenario\n"
        latex += "\\end{enumerate}\n\n"
        latex += "\\vspace{0.5cm}\n\n"
        
        latex += "\\subsection{Final Conclusion}\n\n"
        latex += "\\begin{quote}\n"
        latex += f"\\textit{{This investment is suitable only for {rec['suitable_for'].lower()}.}} "
        latex += "The persistent revenue decline, negative operating margins, and critical cash position present "
        latex += "substantial downside risks. However, the company's IP portfolio, potential for acquisition, "
        latex += "and strong gross margins provide speculative upside for investors willing to accept high risk. "
        latex += f"Given the current trajectory, a \\textbf{{{rec['recommendation']}}} recommendation is warranted.\n"
        latex += "\\end{quote}\n\n"
        
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
\geometry{left=1.2in,right=1.2in,top=1in,bottom=1in}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{float}
\usepackage{setspace}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{parskip}
\onehalfspacing

\definecolor{darkblue}{RGB}{0,51,102}
\definecolor{mediumblue}{RGB}{0,102,204}
\definecolor{lightgray}{RGB}{240,240,240}
\definecolor{darkred}{RGB}{139,0,0}

\titleformat{\section}
  {\normalfont\Large\bfseries\color{darkblue}}
  {\thesection}{1em}{}[\titlerule]

\titleformat{\subsection}
  {\normalfont\large\bfseries\color{mediumblue}}
  {\thesubsection}{1em}{}

\titleformat{\subsubsection}
  {\normalfont\normalsize\bfseries}
  {\thesubsubsection}{1em}{}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textit{GSI Technology - Equity Research}}
\fancyhead[R]{\small\textit{Franciszek Tokarek}}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

\hypersetup{
    colorlinks=true,
    linkcolor=darkblue,
    filecolor=darkblue,
    urlcolor=darkblue,
    citecolor=darkblue
}

\title{
    \vspace{2cm}
    {\Huge\bfseries GSI Technology Inc.}\\[0.5cm]
    {\Large\textcolor{mediumblue}{Comprehensive Equity Research Report}}\\[2cm]
}
\author{
    {\Large\textbf{Franciszek Tokarek}}\\[0.3cm]
    {\normalsize Independent Equity Analysis}
}
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

