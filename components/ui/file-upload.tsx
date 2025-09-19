"use client"

import React, { useRef, useState } from 'react'
import { Button } from './button'
import { Upload, File, X, FileText, Image } from 'lucide-react'

interface FileUploadProps {
  onFileSelect: (file: File) => void
  acceptedTypes?: string[]
  maxSize?: number // in MB
  className?: string
  placeholder?: string
  accept?: string // Alternative prop for HTML accept attribute
}

export function FileUpload({ 
  onFileSelect, 
  acceptedTypes = [], 
  maxSize = 10, 
  className = "",
  placeholder = "Click to upload or drag and drop",
  accept
}: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleFileSelect = (file: File) => {
    if (file.size > maxSize * 1024 * 1024) {
      alert(`File size must be less than ${maxSize}MB`)
      return
    }
    
    // Only validate file types if acceptedTypes is provided and not empty
    if (acceptedTypes && acceptedTypes.length > 0) {
      const fileType = file.type
      const isAccepted = acceptedTypes.some(type => {
        if (type === 'application/pdf') return fileType === 'application/pdf'
        if (type.startsWith('image/')) return fileType.startsWith('image/')
        return fileType === type
      })
      
      if (!isAccepted) {
        alert(`Please select a valid file type: ${acceptedTypes.join(', ')}`)
        return
      }
    }
    
    setSelectedFile(file)
    onFileSelect(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const removeFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const getFileIcon = (file: File) => {
    if (file.type === 'application/pdf') return <FileText className="h-6 w-6 text-red-500" />
    if (file.type.startsWith('image/')) return <Image className="h-6 w-6 text-blue-500" />
    return <File className="h-6 w-6 text-gray-500" />
  }

  return (
    <div className={`w-full ${className}`}>
      <input
        ref={fileInputRef}
        type="file"
        accept={accept || (acceptedTypes && acceptedTypes.length > 0 ? acceptedTypes.join(',') : undefined)}
        onChange={handleFileChange}
        className="hidden"
      />
      
      {!selectedFile ? (
        <div
          onClick={handleClick}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
            ${isDragging 
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/10' 
              : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
            }
          `}
        >
          <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <div className="space-y-2">
            <p className="text-lg font-medium text-gray-700 dark:text-gray-300">
              {placeholder}
            </p>
            {acceptedTypes && acceptedTypes.length > 0 && (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Supported formats: {acceptedTypes.map(type => {
                  if (type === 'application/pdf') return 'PDF'
                  if (type.startsWith('image/')) return 'Images'
                  return type
                }).join(', ')}
              </p>
            )}
            <p className="text-xs text-gray-400">
              Maximum file size: {maxSize}MB
            </p>
          </div>
        </div>
      ) : (
        <div className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {getFileIcon(selectedFile)}
              <div>
                <p className="font-medium text-gray-900 dark:text-gray-100">
                  {selectedFile.name}
                </p>
                <p className="text-sm text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <Button
              onClick={removeFile}
              variant="ghost"
              size="sm"
              className="text-gray-500 hover:text-red-500"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
