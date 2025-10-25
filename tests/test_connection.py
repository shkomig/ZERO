"""
בדיקת חיבור ל-Interactive Brokers
קובץ לבדיקת חיבור, מידע חשבון ונתוני שוק
"""

from ib_insync import IB, Stock, util
import logging
import time

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('trading_connection_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def test_connection():
    """בדיקת חיבור מלאה ל-Interactive Brokers"""
    ib = IB()
    
    try:
        logger.info("🔄 מתחבר ל-Interactive Brokers...")
        logger.info("📍 כתובת: 127.0.0.1:7497, Client ID: 1")
        
        # חיבור ל-IB
        ib.connect('127.0.0.1', 7497, clientId=1)
        logger.info("✅ חיבור הצליח!")
        
        # המתנה קצרה לוודא שהחיבור יציב
        time.sleep(2)
        
        # בדיקת סטטוס חיבור
        logger.info(f"📊 סטטוס חיבור: {ib.isConnected()}")
        
        # בדיקת מידע חשבון
        logger.info("\n" + "="*50)
        logger.info("📋 מידע חשבון")
        logger.info("="*50)
        
        # קבלת מידע חשבון
        account_summary = ib.accountSummary()
        
        if account_summary:
            logger.info("💰 סיכום חשבון:")
            for item in account_summary:
                if item.tag in ['NetLiquidation', 'AvailableFunds', 'BuyingPower', 'TotalCashValue']:
                    logger.info(f"   {item.tag}: {item.value} {item.currency}")
        else:
            logger.warning("⚠️ לא התקבל מידע חשבון")
        
        # בדיקת פוזיציות פתוחות
        logger.info("\n" + "="*50)
        logger.info("📈 פוזיציות פתוחות")
        logger.info("="*50)
        
        positions = ib.positions()
        if positions:
            logger.info(f"🔍 נמצאו {len(positions)} פוזיציות פתוחות:")
            for pos in positions:
                logger.info(f"   📊 {pos.contract.symbol} - כמות: {pos.position}, מחיר ממוצע: {pos.avgCost}")
        else:
            logger.info("📭 אין פוזיציות פתוחות")
        
        # בדיקת נתוני שוק
        logger.info("\n" + "="*50)
        logger.info("📊 בדיקת נתוני שוק")
        logger.info("="*50)
        
        # יצירת חוזה AAPL
        aapl = Stock('AAPL', 'SMART', 'USD')
        
        try:
            logger.info("🔍 מבקש מחיר עבור AAPL...")
            ib.qualifyContracts(aapl)
            
            # קבלת מחיר
            ticker = ib.reqMktData(aapl, '', False, False)
            ib.sleep(3)  # המתנה לקבלת נתונים
            
            if ticker.last:
                logger.info(f"💰 מחיר AAPL: ${ticker.last}")
                logger.info(f"📈 Bid: ${ticker.bid}")
                logger.info(f"📉 Ask: ${ticker.ask}")
                logger.info(f"📊 Volume: {ticker.volume}")
            else:
                logger.warning("⚠️ לא התקבל מחיר עבור AAPL")
                
        except Exception as e:
            logger.error(f"❌ שגיאה בקבלת מחיר AAPL: {e}")
        
        # בדיקת זמן שוק
        logger.info("\n" + "="*50)
        logger.info("🕐 זמן שוק")
        logger.info("="*50)
        
        try:
            # קבלת זמן שוק
            market_data = ib.reqMktData(aapl, '233', False, False)  # זמן שוק
            ib.sleep(2)
            
            if hasattr(market_data, 'marketDataType'):
                logger.info(f"📅 סוג נתוני שוק: {market_data.marketDataType}")
            
            # בדיקה אם השוק פתוח (בדיקה פשוטה)
            import datetime
            now = datetime.datetime.now()
            logger.info(f"🕐 זמן נוכחי: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # בדיקה פשוטה אם זה יום עסקים
            if now.weekday() < 5:  # 0-4 = יום ראשון עד חמישי
                logger.info("📈 השוק אמור להיות פתוח (יום עסקים)")
            else:
                logger.info("📉 השוק סגור (סוף שבוע)")
                
        except Exception as e:
            logger.error(f"❌ שגיאה בבדיקת זמן שוק: {e}")
        
        # בדיקת הרשאות מסחר
        logger.info("\n" + "="*50)
        logger.info("🔐 הרשאות מסחר")
        logger.info("="*50)
        
        try:
            # בדיקת הרשאות חשבון
            account_values = ib.accountValues()
            trading_permissions = [item for item in account_values if 'Trading' in item.tag]
            
            if trading_permissions:
                logger.info("✅ הרשאות מסחר:")
                for perm in trading_permissions:
                    logger.info(f"   {perm.tag}: {perm.value}")
            else:
                logger.info("⚠️ לא נמצאו הרשאות מסחר ספציפיות")
                
        except Exception as e:
            logger.error(f"❌ שגיאה בבדיקת הרשאות: {e}")
        
        logger.info("\n" + "="*50)
        logger.info("✅ בדיקת חיבור הושלמה בהצלחה!")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"❌ שגיאה בחיבור: {e}")
        logger.error(f"🔍 סוג השגיאה: {type(e).__name__}")
        
        # הצעות לפתרון
        logger.info("\n💡 הצעות לפתרון:")
        logger.info("   1. וודא ש-TWS או IB Gateway פועלים")
        logger.info("   2. בדוק שהפורט 7497 פתוח")
        logger.info("   3. וודא שהחיבור מוגדר ל-127.0.0.1")
        logger.info("   4. בדוק שהחשבון פעיל ומאושר למסחר")
        
    finally:
        try:
            if ib.isConnected():
                logger.info("🔌 מנתק מהשרת...")
                ib.disconnect()
                logger.info("✅ ניתוק הושלם")
        except Exception as e:
            logger.error(f"❌ שגיאה בניתוק: {e}")

def test_simple_connection():
    """בדיקת חיבור פשוטה"""
    ib = IB()
    
    try:
        logger.info("🔄 בדיקת חיבור פשוטה...")
        ib.connect('127.0.0.1', 7497, clientId=1)
        logger.info("✅ חיבור בסיסי הצליח!")
        
        # בדיקה מהירה של סטטוס
        logger.info(f"📊 חיבור פעיל: {ib.isConnected()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ חיבור בסיסי נכשל: {e}")
        return False
        
    finally:
        if ib.isConnected():
            ib.disconnect()

if __name__ == '__main__':
    logger.info("🚀 מתחיל בדיקת חיבור ל-Interactive Brokers")
    logger.info("="*60)
    
    # בדיקה פשוטה קודם
    if test_simple_connection():
        logger.info("\n🔄 עובר לבדיקה מלאה...")
        test_connection()
    else:
        logger.error("❌ בדיקה בסיסית נכשלה - לא ממשיך לבדיקה מלאה")
    
    logger.info("\n🏁 בדיקת חיבור הושלמה")
