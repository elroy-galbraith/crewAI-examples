from crewai.tools import BaseTool
from typing import Type, Any, Dict, List
from pydantic import BaseModel, Field
import os


class FinancialReportRAGInput(BaseModel):
    """Input schema for Financial Report RAG Tool."""
    company_name: str = Field(..., description="Name of the company to search for")
    query: str = Field(..., description="Specific query about the company's financial reports")


class FinancialReportRAGTool(BaseTool):
    name: str = "Financial Report RAG Tool"
    description: str = (
        "Retrieves information from financial reports (10-K, 10-Q, annual reports) "
        "using RAG (Retrieval Augmented Generation). Provide the company name and "
        "your specific query to get relevant financial information."
    )
    args_schema: Type[BaseModel] = FinancialReportRAGInput

    def _run(self, company_name: str, query: str) -> str:
        """
        Execute RAG search on financial reports.
        
        In a production implementation, this would:
        1. Connect to a vector database with embedded financial reports
        2. Perform semantic search for relevant chunks
        3. Return contextual information
        
        For now, this is a placeholder implementation.
        """
        # TODO: Implement actual RAG logic with vector database
        # This could use ChromaDB, Pinecone, or similar
        
        return f"""
        [RAG Search Results for {company_name}]
        Query: {query}
        
        Note: This is a placeholder. In production, this would return actual financial data
        from embedded 10-K/10-Q reports, annual reports, and other SEC filings.
        
        To implement:
        - Set up vector database with financial report embeddings
        - Index SEC EDGAR filings
        - Perform semantic search based on query
        - Return relevant chunks with citations
        """


class RatioCalculatorInput(BaseModel):
    """Input schema for Ratio Calculator Tool."""
    financial_data: Dict[str, float] = Field(
        ...,
        description="Dictionary of financial metrics needed for calculation"
    )
    ratio_type: str = Field(
        ...,
        description="Type of ratio to calculate: PE, PB, ROE, ROA, Current, Quick, Debt_to_Equity, etc."
    )


class RatioCalculatorTool(BaseTool):
    name: str = "Ratio Calculator"
    description: str = (
        "Calculates financial ratios from provided financial data. "
        "Supports: P/E, P/B, ROE, ROA, Current Ratio, Quick Ratio, "
        "Debt-to-Equity, Gross Margin, Operating Margin, Net Margin, and more."
    )
    args_schema: Type[BaseModel] = RatioCalculatorInput

    def _run(self, financial_data: Dict[str, float], ratio_type: str) -> Dict[str, Any]:
        """
        Calculate financial ratios.
        
        Args:
            financial_data: Dictionary with financial metrics
            ratio_type: Type of ratio to calculate
        
        Returns:
            Dictionary with calculation results and interpretation
        """
        ratio_type = ratio_type.upper().replace(" ", "_")
        
        try:
            result = {}
            
            if ratio_type == "PE" or ratio_type == "P/E":
                price = financial_data.get("price", 0)
                eps = financial_data.get("eps", 0)
                if eps != 0:
                    result["value"] = round(price / eps, 2)
                    result["formula"] = "Price / EPS"
                    result["interpretation"] = self._interpret_pe(result["value"])
                
            elif ratio_type == "PB" or ratio_type == "P/B":
                price = financial_data.get("price", 0)
                book_value_per_share = financial_data.get("book_value_per_share", 0)
                if book_value_per_share != 0:
                    result["value"] = round(price / book_value_per_share, 2)
                    result["formula"] = "Price / Book Value per Share"
                    result["interpretation"] = self._interpret_pb(result["value"])
            
            elif ratio_type == "ROE":
                net_income = financial_data.get("net_income", 0)
                shareholders_equity = financial_data.get("shareholders_equity", 0)
                if shareholders_equity != 0:
                    result["value"] = round((net_income / shareholders_equity) * 100, 2)
                    result["formula"] = "(Net Income / Shareholders' Equity) × 100"
                    result["interpretation"] = self._interpret_roe(result["value"])
            
            elif ratio_type == "ROA":
                net_income = financial_data.get("net_income", 0)
                total_assets = financial_data.get("total_assets", 0)
                if total_assets != 0:
                    result["value"] = round((net_income / total_assets) * 100, 2)
                    result["formula"] = "(Net Income / Total Assets) × 100"
                    result["interpretation"] = self._interpret_roa(result["value"])
            
            elif ratio_type == "CURRENT_RATIO":
                current_assets = financial_data.get("current_assets", 0)
                current_liabilities = financial_data.get("current_liabilities", 0)
                if current_liabilities != 0:
                    result["value"] = round(current_assets / current_liabilities, 2)
                    result["formula"] = "Current Assets / Current Liabilities"
                    result["interpretation"] = self._interpret_current_ratio(result["value"])
            
            elif ratio_type == "DEBT_TO_EQUITY":
                total_debt = financial_data.get("total_debt", 0)
                shareholders_equity = financial_data.get("shareholders_equity", 0)
                if shareholders_equity != 0:
                    result["value"] = round(total_debt / shareholders_equity, 2)
                    result["formula"] = "Total Debt / Shareholders' Equity"
                    result["interpretation"] = self._interpret_debt_to_equity(result["value"])
            
            else:
                result["error"] = f"Ratio type '{ratio_type}' not supported"
                result["supported_ratios"] = [
                    "PE", "PB", "ROE", "ROA", "CURRENT_RATIO", "DEBT_TO_EQUITY"
                ]
            
            result["ratio_type"] = ratio_type
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "ratio_type": ratio_type,
                "financial_data": financial_data
            }
    
    def _interpret_pe(self, value: float) -> str:
        if value < 15:
            return "Low P/E - potentially undervalued or declining business"
        elif value < 25:
            return "Moderate P/E - reasonably valued"
        else:
            return "High P/E - growth expectations or potentially overvalued"
    
    def _interpret_pb(self, value: float) -> str:
        if value < 1:
            return "P/B < 1 - trading below book value, potential value opportunity"
        elif value < 3:
            return "Moderate P/B ratio"
        else:
            return "High P/B - premium valuation or asset-light business"
    
    def _interpret_roe(self, value: float) -> str:
        if value < 10:
            return "Low ROE - poor profitability"
        elif value < 20:
            return "Moderate ROE - acceptable profitability"
        else:
            return "High ROE - strong profitability"
    
    def _interpret_roa(self, value: float) -> str:
        if value < 5:
            return "Low ROA - inefficient asset usage"
        elif value < 10:
            return "Moderate ROA"
        else:
            return "High ROA - efficient asset usage"
    
    def _interpret_current_ratio(self, value: float) -> str:
        if value < 1:
            return "Current Ratio < 1 - liquidity concerns"
        elif value < 2:
            return "Adequate liquidity"
        else:
            return "Strong liquidity position"
    
    def _interpret_debt_to_equity(self, value: float) -> str:
        if value < 0.5:
            return "Low leverage - conservative capital structure"
        elif value < 1.5:
            return "Moderate leverage"
        else:
            return "High leverage - increased financial risk"


class VisualizationInput(BaseModel):
    """Input schema for Visualization Tool."""
    data: Dict[str, Any] = Field(
        ...,
        description="Data to visualize with 'labels' (list of strings) and 'values' (list of numbers). Example: {'labels': ['Q1', 'Q2', 'Q3'], 'values': [100, 150, 200]}"
    )
    chart_type: str = Field(
        ...,
        description="Type of chart: line, bar, pie, scatter"
    )
    title: str = Field(..., description="Chart title")
    filename: str = Field(..., description="Output filename (without extension)")


class VisualizationTool(BaseTool):
    name: str = "Visualization Tool"
    description: str = (
        "Creates financial visualizations (charts and graphs). "
        "Supports line charts, bar charts, pie charts, and scatter plots. "
        "Saves charts as PNG files and returns the file path."
    )
    args_schema: Type[BaseModel] = VisualizationInput

    def _run(
        self,
        data: Dict[str, Any],
        chart_type: str,
        title: str,
        filename: str
    ) -> str:
        """
        Create a visualization.
        
        In production, this would use matplotlib or plotly to create charts.
        For now, returns a placeholder.
        """
        # TODO: Implement actual visualization with matplotlib/plotly
        
        output_path = f"./visualizations/{filename}.png"
        
        return f"""
        [Visualization Created]
        Type: {chart_type}
        Title: {title}
        Output: {output_path}
        Data Points: {len(data.get('values', []))}
        
        Note: This is a placeholder. In production, this would:
        - Use matplotlib or plotly to create the chart
        - Save to {output_path}
        - Return the actual file path
        
        Sample implementation:
        ```python
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        # Create chart based on chart_type
        plt.title(title)
        plt.savefig(output_path)
        plt.close()
        ```
        """
