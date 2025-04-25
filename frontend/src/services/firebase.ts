import { initializeApp, getApps, getApp } from 'firebase/app';
import { getFirestore, collection, getDocs, getDoc, addDoc, updateDoc, deleteDoc, doc, query, where, orderBy, limit, startAfter, DocumentData, QueryDocumentSnapshot } from 'firebase/firestore';
import { Property, PropertyCreate, PropertyUpdate } from '@/types/property';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID
};

// Initialize Firebase
const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
const db = getFirestore(app);

const convertToProperty = (doc: QueryDocumentSnapshot<DocumentData>): Property => {
  const data = doc.data();
  return {
    id: doc.id,
    title: data.title,
    description: data.description,
    price: data.price,
    location: data.location,
    bedrooms: data.bedrooms,
    bathrooms: data.bathrooms,
    area: data.area,
    images: data.images || [],
    property_type: data.property_type,
    status: data.status
  };
};

export const firestoreService = {
  async getProperties(
    pageSize: number = 10,
    lastVisible?: QueryDocumentSnapshot<DocumentData>,
    filters?: {
      propertyType?: string;
      minPrice?: number;
      maxPrice?: number;
      location?: string;
    }
  ): Promise<{ properties: Property[]; lastVisible: QueryDocumentSnapshot<DocumentData> | undefined }> {
    try {
      console.log('Fetching properties from Firestore...');
      let q = collection(db, 'properties');
      console.log('Collection reference:', q);
      
      // Build query with filters
      const conditions = [];
      if (filters?.propertyType) {
        conditions.push(where('property_type', '==', filters.propertyType));
      }
      if (filters?.minPrice) {
        conditions.push(where('price', '>=', filters.minPrice));
      }
      if (filters?.maxPrice) {
        conditions.push(where('price', '<=', filters.maxPrice));
      }
      if (filters?.location) {
        conditions.push(where('location', '==', filters.location));
      }

      q = query(
        q,
        ...conditions,
        orderBy('createdAt', 'desc'),
        limit(pageSize)
      );

      if (lastVisible) {
        q = query(q, startAfter(lastVisible));
      }

      const snapshot = await getDocs(q);
      console.log('Number of documents retrieved:', snapshot.docs.length);
      const properties = snapshot.docs.map(convertToProperty);
      console.log('Converted properties:', properties);
      
      const newLastVisible = snapshot.docs[snapshot.docs.length - 1];
      return {
        properties,
        lastVisible: newLastVisible
      };
    } catch (error) {
      console.error('Error fetching properties:', error);
      if (error instanceof Error) {
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
      }
      return { properties: [], lastVisible: undefined };
    }
  },

  async getProperty(id: string): Promise<Property | null> {
    try {
      const docRef = doc(db, 'properties', id);
      const docSnap = await getDoc(docRef);

      if (docSnap.exists()) {
        return convertToProperty(docSnap as QueryDocumentSnapshot<DocumentData>);
      }
      return null;
    } catch (error) {
      console.error('Error fetching property:', error);
      return null;
    }
  },

  async createProperty(property: PropertyCreate): Promise<Property | null> {
    try {
      console.log('Starting property creation with data:', property);
      
      // Verify Firestore is initialized
      if (!db) {
        console.error('Firestore database is not initialized');
        return null;
      }

      const propertyWithTimestamp = {
        ...property,
        status: 'available',
        createdAt: new Date(),
        updatedAt: new Date()
      };

      console.log('Attempting to add document to Firestore...');
      const propertiesCollection = collection(db, 'properties');
      console.log('Properties collection reference:', propertiesCollection);
      
      const docRef = await addDoc(propertiesCollection, propertyWithTimestamp);
      console.log('Document added with ID:', docRef.id);

      // Verify the document was created
      const newDoc = await getDoc(docRef);
      console.log('Document exists after creation:', newDoc.exists());
      console.log('Document data:', newDoc.data());
      
      if (newDoc.exists()) {
        const createdProperty = convertToProperty(newDoc as QueryDocumentSnapshot<DocumentData>);
        console.log('Successfully created and retrieved property:', createdProperty);
        return createdProperty;
      }
      
      console.error('Document does not exist after creation attempt');
      return null;
    } catch (error) {
      console.error('Error in createProperty:', error);
      if (error instanceof Error) {
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
      }
      return null;
    }
  },

  async updateProperty(id: string, property: PropertyUpdate): Promise<Property | null> {
    try {
      const docRef = doc(db, 'properties', id);
      const updateData = {
        ...property,
        updatedAt: new Date()
      };
      
      await updateDoc(docRef, updateData);
      const updatedDoc = await getDoc(docRef);
      
      if (updatedDoc.exists()) {
        return convertToProperty(updatedDoc as QueryDocumentSnapshot<DocumentData>);
      }
      return null;
    } catch (error) {
      console.error('Error updating property:', error);
      return null;
    }
  },

  async deleteProperty(id: string): Promise<boolean> {
    try {
      const docRef = doc(db, 'properties', id);
      await deleteDoc(docRef);
      return true;
    } catch (error) {
      console.error('Error deleting property:', error);
      return false;
    }
  }
}; 