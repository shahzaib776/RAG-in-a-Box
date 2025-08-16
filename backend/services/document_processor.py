import os
import tempfile
from typing import List, Dict, Any
from pathlib import Path
import base64
from io import BytesIO

from unstructured.partition.pdf import partition_pdf
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

class DocumentProcessor:
    def __init__(self):
        """Initialize the document processor with vision model"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load BLIP model for image captioning
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
        self.blip_model.to(self.device)
    
    async def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a PDF document and extract text, tables, and images"""
        chunks = []
        
        try:
            # Create temporary directory for extracted images
            with tempfile.TemporaryDirectory() as temp_dir:
                # Partition PDF with image extraction
                elements = partition_pdf(
                    filename=file_path,
                    extract_images_in_pdf=True,
                    infer_table_structure=True,
                    chunking_strategy="by_title",
                    max_characters=1000,
                    new_after_n_chars=800,
                    combine_text_under_n_chars=500,
                    extract_image_block_output_dir=temp_dir
                )
                
                # Process each element
                for i, element in enumerate(elements):
                    chunk = {
                        'id': f"chunk_{i}",
                        'type': str(type(element).__name__),
                        'content': str(element),
                        'metadata': element.metadata.to_dict() if hasattr(element, 'metadata') else {}
                    }
                    
                    # Handle different element types
                    if hasattr(element, 'text'):
                        chunk['content'] = element.text
                    
                    chunks.append(chunk)
                
                # Process extracted images
                image_chunks = await self._process_extracted_images(temp_dir)
                chunks.extend(image_chunks)
                
        except Exception as e:
            print(f"Error processing document: {e}")
            # Fallback: simple text extraction
            chunks = await self._fallback_text_extraction(file_path)
        
        return chunks
    
    async def _process_extracted_images(self, temp_dir: str) -> List[Dict[str, Any]]:
        """Process extracted images and generate captions"""
        image_chunks = []
        
        # Look for extracted images
        for image_file in Path(temp_dir).glob("*.jpg"):
            try:
                # Load and process image
                image = Image.open(image_file).convert('RGB')
                
                # Generate caption using BLIP
                inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    out = self.blip_model.generate(**inputs, max_length=100, num_beams=5)
                    caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
                
                # Create image chunk
                chunk = {
                    'id': f"image_{image_file.stem}",
                    'type': 'Image',
                    'content': f"Image description: {caption}",
                    'metadata': {
                        'image_path': str(image_file),
                        'caption': caption,
                        'content_type': 'image'
                    }
                }
                
                image_chunks.append(chunk)
                
            except Exception as e:
                print(f"Error processing image {image_file}: {e}")
                continue
        
        return image_chunks
    
    async def _fallback_text_extraction(self, file_path: str) -> List[Dict[str, Any]]:
        """Fallback method for simple text extraction"""
        try:
            elements = partition_pdf(filename=file_path)
            chunks = []
            
            for i, element in enumerate(elements):
                chunk = {
                    'id': f"fallback_chunk_{i}",
                    'type': 'Text',
                    'content': str(element),
                    'metadata': {}
                }
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            print(f"Fallback extraction failed: {e}")
            return [{
                'id': 'error_chunk',
                'type': 'Error',
                'content': 'Failed to extract content from PDF',
                'metadata': {'error': str(e)}
            }]