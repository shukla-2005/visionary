from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import os
from app.services.stock_service import StockService
from app.services.prediction_service import PredictionService
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/{ticker}")
async def generate_report(
    ticker: str,
    format: str = "csv",
    current_user: User = Depends(get_current_user)
):
    try:
        # Get stock data
        stock_info = StockService.get_stock_info(ticker)
        historical_data = StockService.get_historical_data(ticker)

        if not stock_info or not historical_data:
            raise HTTPException(status_code=404, detail="Stock data not available")

        # Generate report file
        report_path = f"reports/{ticker}_report.{format}"

        if format == "csv":
            import pandas as pd
            df = pd.DataFrame([{
                'date': h.date,
                'open': h.open,
                'high': h.high,
                'low': h.low,
                'close': h.close,
                'volume': h.volume,
                'adj_close': h.adj_close
            } for h in historical_data])

            os.makedirs("reports", exist_ok=True)
            df.to_csv(report_path, index=False)

        elif format == "pdf":
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter

                os.makedirs("reports", exist_ok=True)
                c = canvas.Canvas(report_path, pagesize=letter)

                # Add content to PDF
                c.drawString(100, 750, f"Stock Report for {ticker}")
                c.drawString(100, 730, f"Company: {stock_info.name}")
                c.drawString(100, 710, f"Current Price: ${stock_info.current_price:.2f}")
                c.drawString(100, 690, f"Market Cap: {stock_info.market_cap}")

                c.save()
            except ImportError:
                raise HTTPException(status_code=400, detail="PDF generation requires reportlab. Please use CSV format.")

        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'csv' or 'pdf'")

        return FileResponse(
            report_path,
            media_type='application/octet-stream',
            filename=f"{ticker}_report.{format}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))