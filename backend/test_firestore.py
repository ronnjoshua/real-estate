import asyncio
import logging
from app.services.firestore import FirestoreService
from app.core.firebase import initialize_firebase

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_firestore():
    logger.info("Initializing Firebase...")
    initialize_firebase()
    
    logger.info("Creating FirestoreService...")
    fs = FirestoreService()
    
    logger.info("Attempting to fetch properties from Firestore...")
    try:
        props = await fs.get_all_properties()
        logger.info(f"Found {len(props)} properties")
        for i, prop in enumerate(props):
            logger.info(f"Property {i+1}: {prop.get('title', 'No title')} - {prop.get('id', 'No ID')}")
    except Exception as e:
        logger.error(f"Error fetching properties: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_firestore()) 