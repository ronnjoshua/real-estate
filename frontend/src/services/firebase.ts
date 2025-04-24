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
      let q = collection(db, 'properties');
      
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
      const properties = snapshot.docs.map(convertToProperty);
      const newLastVisible = snapshot.docs[snapshot.docs.length - 1];

      return {
        properties,
        lastVisible: newLastVisible
      };
    } catch (error) {
      console.error('Error fetching properties:', error);
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
      const propertyWithTimestamp = {
        ...property,
        createdAt: new Date(),
        updatedAt: new Date()
      };

      const docRef = await addDoc(collection(db, 'properties'), propertyWithTimestamp);
      const newDoc = await getDoc(docRef);
      
      if (newDoc.exists()) {
        return convertToProperty(newDoc as QueryDocumentSnapshot<DocumentData>);
      }
      return null;
    } catch (error) {
      console.error('Error creating property:', error);
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