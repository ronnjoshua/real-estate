'use client';

import { useRef, useState, useCallback } from 'react';
import Image from 'next/image';

interface CloudinaryUploadProps {
  images: string[];
  onImagesChange: (images: string[]) => void;
  maxImages?: number;
}

declare global {
  interface Window {
    cloudinary?: {
      createUploadWidget: (
        options: Record<string, unknown>,
        callback: (error: Error | null, result: { event: string; info: { secure_url: string } }) => void
      ) => { open: () => void; destroy: () => void };
    };
  }
}

const CLOUD_NAME = 'djf3rir7i';
const UPLOAD_PRESET = 'real_estate_unsigned';

export default function CloudinaryUpload({ images, onImagesChange, maxImages = 10 }: CloudinaryUploadProps) {
  const [isLoading, setIsLoading] = useState(false);
  const widgetRef = useRef<{ open: () => void; destroy: () => void } | null>(null);
  const imagesRef = useRef(images);

  // Keep ref updated
  imagesRef.current = images;

  const loadScriptAndOpenWidget = useCallback(() => {
    const openWidget = () => {
      if (widgetRef.current) {
        widgetRef.current.open();
        return;
      }

      if (!window.cloudinary) return;

      widgetRef.current = window.cloudinary.createUploadWidget(
        {
          cloudName: CLOUD_NAME,
          uploadPreset: UPLOAD_PRESET,
          sources: ['local', 'url', 'camera'],
          multiple: true,
          maxFiles: maxImages - imagesRef.current.length,
          resourceType: 'image',
          clientAllowedFormats: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
          maxFileSize: 10000000,
          folder: 'real-estate',
          cropping: false,
          showPoweredBy: false,
          styles: {
            palette: {
              window: '#FFFFFF',
              windowBorder: '#90A0B3',
              tabIcon: '#2563EB',
              menuIcons: '#5A616A',
              textDark: '#000000',
              textLight: '#FFFFFF',
              link: '#2563EB',
              action: '#2563EB',
              inactiveTabIcon: '#6B7280',
              error: '#DC2626',
              inProgress: '#2563EB',
              complete: '#16A34A',
              sourceBg: '#F3F4F6'
            }
          }
        },
        (error, result) => {
          if (error) {
            console.error('Upload error:', error);
            setIsLoading(false);
            return;
          }

          if (result.event === 'success') {
            const newUrl = result.info.secure_url;
            onImagesChange([...imagesRef.current, newUrl]);
          }

          if (result.event === 'close') {
            setIsLoading(false);
          }
        }
      );

      widgetRef.current.open();
    };

    // Check if script already loaded
    if (window.cloudinary) {
      openWidget();
      return;
    }

    // Load script
    const existingScript = document.querySelector('script[src*="cloudinary"]');
    if (existingScript) {
      // Wait for it to load
      const checkInterval = setInterval(() => {
        if (window.cloudinary) {
          clearInterval(checkInterval);
          openWidget();
        }
      }, 100);
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://widget.cloudinary.com/v2.0/global/all.js';
    script.async = true;
    script.onload = openWidget;
    document.body.appendChild(script);
  }, [maxImages, onImagesChange]);

  const handleOpenWidget = useCallback(() => {
    setIsLoading(true);
    loadScriptAndOpenWidget();
  }, [loadScriptAndOpenWidget]);

  const handleRemoveImage = useCallback((indexToRemove: number) => {
    onImagesChange(images.filter((_, index) => index !== indexToRemove));
  }, [images, onImagesChange]);

  const handleMoveImage = useCallback((fromIndex: number, direction: 'up' | 'down') => {
    const toIndex = direction === 'up' ? fromIndex - 1 : fromIndex + 1;
    if (toIndex < 0 || toIndex >= images.length) return;

    const newImages = [...images];
    [newImages[fromIndex], newImages[toIndex]] = [newImages[toIndex], newImages[fromIndex]];
    onImagesChange(newImages);
  }, [images, onImagesChange]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          Property Images ({images.length}/{maxImages})
        </label>
        <button
          type="button"
          onClick={handleOpenWidget}
          disabled={isLoading || images.length >= maxImages}
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
              Opening...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Upload Images
            </>
          )}
        </button>
      </div>

      {images.length === 0 ? (
        <div
          onClick={handleOpenWidget}
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
        >
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="mt-2 text-sm text-gray-600">Click to upload property images</p>
          <p className="text-xs text-gray-500 mt-1">PNG, JPG, GIF, WEBP up to 10MB</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {images.map((url, index) => (
            <div key={`${url}-${index}`} className="relative group">
              <div className="relative h-32 rounded-lg overflow-hidden border border-gray-200">
                <Image
                  src={url}
                  alt={`Property image ${index + 1}`}
                  fill
                  style={{ objectFit: 'cover' }}
                  sizes="(max-width: 768px) 50vw, 25vw"
                />
                {index === 0 && (
                  <div className="absolute top-2 left-2 bg-blue-600 text-white text-xs px-2 py-1 rounded">
                    Main
                  </div>
                )}
              </div>

              <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center gap-2">
                {index > 0 && (
                  <button
                    type="button"
                    onClick={() => handleMoveImage(index, 'up')}
                    className="p-1 bg-white rounded-full hover:bg-gray-100"
                    title="Move left"
                  >
                    <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </button>
                )}

                <button
                  type="button"
                  onClick={() => handleRemoveImage(index)}
                  className="p-1 bg-red-500 rounded-full hover:bg-red-600"
                  title="Remove image"
                >
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>

                {index < images.length - 1 && (
                  <button
                    type="button"
                    onClick={() => handleMoveImage(index, 'down')}
                    className="p-1 bg-white rounded-full hover:bg-gray-100"
                    title="Move right"
                  >
                    <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
          ))}

          {images.length < maxImages && (
            <div
              onClick={handleOpenWidget}
              className="h-32 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="text-xs text-gray-500 mt-1">Add more</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
