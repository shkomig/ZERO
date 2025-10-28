"""
Advanced Computer Vision Agent for Zero Agent
Provides AI-powered screen understanding and element detection
"""

import cv2
import numpy as np
from PIL import Image
import torch
from transformers import pipeline
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ColorAnalyzer:
    """Analyze dominant colors in images"""
    
    def get_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[Dict]:
        """Get dominant colors using K-means clustering"""
        try:
            from sklearn.cluster import KMeans
            
            # Reshape image to be a list of pixels
            pixels = image.reshape(-1, 3)
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(pixels)
            
            # Get cluster centers (dominant colors)
            colors = kmeans.cluster_centers_.astype(int)
            labels = kmeans.labels_
            
            # Calculate color percentages
            color_counts = np.bincount(labels)
            color_percentages = color_counts / len(labels) * 100
            
            dominant_colors = []
            for i, color in enumerate(colors):
                dominant_colors.append({
                    "rgb": color.tolist(),
                    "hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",
                    "percentage": round(color_percentages[i], 2)
                })
            
            return dominant_colors
            
        except ImportError:
            logger.warning("scikit-learn not available, using simple color analysis")
            return self._simple_color_analysis(image, k)
        except Exception as e:
            logger.error(f"Color analysis failed: {e}")
            return []
    
    def _simple_color_analysis(self, image: np.ndarray, k: int = 5) -> List[Dict]:
        """Simple color analysis without sklearn"""
        # Sample random pixels
        h, w = image.shape[:2]
        sample_size = min(1000, h * w)
        
        # Get random pixel indices
        indices = np.random.choice(h * w, sample_size, replace=False)
        pixels = image.reshape(-1, 3)[indices]
        
        # Simple histogram-based analysis
        colors = []
        for channel in range(3):
            hist, bins = np.histogram(pixels[:, channel], bins=k)
            peak_indices = np.argsort(hist)[-k:][::-1]
            for idx in peak_indices:
                color_value = int(bins[idx])
                colors.append({
                    "rgb": [color_value if i == channel else 0 for i in range(3)],
                    "hex": f"#{color_value:02x}0000" if channel == 0 else f"#00{color_value:02x}00" if channel == 1 else f"#0000{color_value:02x}",
                    "percentage": round(hist[idx] / sample_size * 100, 2)
                })
        
        return colors[:k]


class VisionAgent:
    """
    Advanced Computer Vision Agent
    
    Capabilities:
    - Object detection and recognition
    - OCR text extraction
    - UI element detection
    - Layout analysis
    - Color analysis
    - Natural language element finding
    """
    
    def __init__(self, llm=None):
        self.llm = llm
        self.color_analyzer = ColorAnalyzer()
        
        # Initialize models (with fallbacks)
        self._init_models()
        
        logger.info("Vision Agent initialized")
    
    def _init_models(self):
        """Initialize AI models with fallbacks"""
        try:
            # Object detection
            self.object_detector = pipeline(
                "object-detection", 
                model="facebook/detr-resnet-50",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Object detection model loaded")
        except Exception as e:
            logger.warning(f"Object detection model failed: {e}")
            self.object_detector = None
        
        try:
            # OCR
            self.ocr_reader = pipeline(
                "image-to-text", 
                model="microsoft/trocr-base-printed",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("OCR model loaded")
        except Exception as e:
            logger.warning(f"OCR model failed: {e}")
            self.ocr_reader = None
        
        try:
            # Image classification
            self.image_classifier = pipeline(
                "image-classification", 
                model="google/vit-base-patch16-224",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Image classification model loaded")
        except Exception as e:
            logger.warning(f"Image classification model failed: {e}")
            self.image_classifier = None
    
    def analyze_screen(self, screenshot_path: str) -> Dict:
        """
        Comprehensive screen analysis
        
        Args:
            screenshot_path: Path to screenshot image
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Load image
            image = cv2.imread(screenshot_path)
            if image is None:
                raise ValueError(f"Could not load image: {screenshot_path}")
            
            # Convert BGR to RGB for models
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "image_path": screenshot_path,
                "image_size": image.shape[:2],
                "objects": [],
                "text": [],
                "ui_elements": [],
                "colors": [],
                "layout": {},
                "success": True
            }
            
            # 1. Object Detection
            if self.object_detector:
                try:
                    objects = self.object_detector(image_rgb)
                    analysis["objects"] = objects
                    logger.info(f"Detected {len(objects)} objects")
                except Exception as e:
                    logger.warning(f"Object detection failed: {e}")
            
            # 2. OCR Text Extraction
            if self.ocr_reader:
                try:
                    text_result = self.ocr_reader(image_rgb)
                    analysis["text"] = text_result
                    logger.info(f"Extracted {len(text_result)} text elements")
                except Exception as e:
                    logger.warning(f"OCR failed: {e}")
            
            # 3. UI Element Detection
            ui_elements = self._detect_ui_elements(image)
            analysis["ui_elements"] = ui_elements
            logger.info(f"Detected {len(ui_elements)} UI elements")
            
            # 4. Color Analysis
            colors = self.color_analyzer.get_dominant_colors(image)
            analysis["colors"] = colors
            logger.info(f"Analyzed {len(colors)} dominant colors")
            
            # 5. Layout Analysis
            layout = self._analyze_layout(image)
            analysis["layout"] = layout
            
            return analysis
            
        except Exception as e:
            logger.error(f"Screen analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _detect_ui_elements(self, image: np.ndarray) -> List[Dict]:
        """Detect UI elements like buttons, inputs, menus"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            ui_elements = []
            for contour in contours:
                # Filter small contours
                area = cv2.contourArea(contour)
                if area < 100:  # Minimum area threshold
                    continue
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter very small elements
                if w < 20 or h < 20:
                    continue
                
                # Extract element region
                element_region = image[y:y+h, x:x+w]
                
                # Classify element type
                element_type = self._classify_element(element_region)
                
                # Calculate element properties
                aspect_ratio = w / h
                center_x = x + w // 2
                center_y = y + h // 2
                
                ui_elements.append({
                    "type": element_type,
                    "coordinates": (x, y, w, h),
                    "center": (center_x, center_y),
                    "area": area,
                    "aspect_ratio": round(aspect_ratio, 2),
                    "confidence": 0.8  # Default confidence
                })
            
            # Sort by area (largest first)
            ui_elements.sort(key=lambda x: x["area"], reverse=True)
            
            return ui_elements[:20]  # Return top 20 elements
            
        except Exception as e:
            logger.error(f"UI element detection failed: {e}")
            return []
    
    def _classify_element(self, element_region: np.ndarray) -> str:
        """Classify UI element type"""
        try:
            h, w = element_region.shape[:2]
            aspect_ratio = w / h
            
            # Simple heuristic classification
            if aspect_ratio > 3:
                return "input_field"
            elif aspect_ratio < 0.5:
                return "button_vertical"
            elif h > 50 and w > 100:
                return "button_large"
            elif h < 30 and w < 100:
                return "button_small"
            elif h > 100:
                return "menu_item"
            else:
                return "ui_element"
                
        except Exception as e:
            logger.warning(f"Element classification failed: {e}")
            return "unknown"
    
    def _analyze_layout(self, image: np.ndarray) -> Dict:
        """Analyze screen layout structure"""
        try:
            h, w = image.shape[:2]
            
            # Detect horizontal and vertical lines
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Horizontal lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (w//4, 1))
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Vertical lines
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, h//4))
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
            
            # Count lines
            h_line_count = len(cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0])
            v_line_count = len(cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0])
            
            # Determine layout type
            if h_line_count > 3 and v_line_count > 3:
                layout_type = "grid"
            elif h_line_count > 3:
                layout_type = "horizontal_blocks"
            elif v_line_count > 3:
                layout_type = "vertical_blocks"
            else:
                layout_type = "freeform"
            
            return {
                "type": layout_type,
                "horizontal_lines": h_line_count,
                "vertical_lines": v_line_count,
                "width": w,
                "height": h,
                "density": (h_line_count + v_line_count) / (w * h) * 10000
            }
            
        except Exception as e:
            logger.warning(f"Layout analysis failed: {e}")
            return {"type": "unknown", "error": str(e)}
    
    def find_element(self, description: str, screenshot_path: str) -> Dict:
        """
        Find UI element by natural language description
        
        Args:
            description: Natural language description of element
            screenshot_path: Path to screenshot
            
        Returns:
            Dictionary with element information
        """
        try:
            # Analyze screen first
            analysis = self.analyze_screen(screenshot_path)
            
            if not analysis.get("success", False):
                return {
                    "success": False,
                    "error": "Screen analysis failed",
                    "element": None
                }
            
            # Use LLM to match description to elements
            if self.llm:
                element = self._llm_find_element(description, analysis)
            else:
                element = self._heuristic_find_element(description, analysis)
            
            return {
                "success": element is not None,
                "element": element,
                "description": description,
                "confidence": element.get("confidence", 0.0) if element else 0.0
            }
            
        except Exception as e:
            logger.error(f"Element finding failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "element": None
            }
    
    def _llm_find_element(self, description: str, analysis: Dict) -> Optional[Dict]:
        """Use LLM to find element by description"""
        try:
            prompt = f"""
            Find UI element matching this description: "{description}"
            
            Available UI elements:
            {json.dumps(analysis['ui_elements'], indent=2)}
            
            Available text elements:
            {json.dumps(analysis['text'], indent=2)}
            
            Return the best matching element in this format:
            {{
                "type": "element_type",
                "coordinates": [x, y, w, h],
                "center": [center_x, center_y],
                "confidence": 0.0-1.0,
                "reason": "why this element matches"
            }}
            
            If no good match found, return null.
            """
            
            result = self.llm.generate(prompt)
            
            # Parse LLM response
            try:
                element_data = json.loads(result)
                if element_data and element_data.get("coordinates"):
                    return element_data
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response as JSON")
            
            return None
            
        except Exception as e:
            logger.warning(f"LLM element finding failed: {e}")
            return None
    
    def _heuristic_find_element(self, description: str, analysis: Dict) -> Optional[Dict]:
        """Heuristic element finding without LLM"""
        try:
            description_lower = description.lower()
            ui_elements = analysis.get("ui_elements", [])
            
            # Simple keyword matching
            for element in ui_elements:
                element_type = element.get("type", "").lower()
                
                # Check for type matches
                if any(keyword in description_lower for keyword in ["button", "כפתור"]):
                    if "button" in element_type:
                        element["confidence"] = 0.8
                        element["reason"] = "Button type match"
                        return element
                
                if any(keyword in description_lower for keyword in ["input", "field", "שדה", "קלט"]):
                    if "input" in element_type:
                        element["confidence"] = 0.8
                        element["reason"] = "Input field type match"
                        return element
                
                if any(keyword in description_lower for keyword in ["menu", "תפריט"]):
                    if "menu" in element_type:
                        element["confidence"] = 0.8
                        element["reason"] = "Menu type match"
                        return element
            
            # Return largest element as fallback
            if ui_elements:
                largest = max(ui_elements, key=lambda x: x.get("area", 0))
                largest["confidence"] = 0.3
                largest["reason"] = "Largest element (fallback)"
                return largest
            
            return None
            
        except Exception as e:
            logger.warning(f"Heuristic element finding failed: {e}")
            return None
    
    def get_screen_summary(self, screenshot_path: str) -> str:
        """Get human-readable screen summary"""
        try:
            analysis = self.analyze_screen(screenshot_path)
            
            if not analysis.get("success", False):
                return f"Screen analysis failed: {analysis.get('error', 'Unknown error')}"
            
            summary_parts = []
            
            # Basic info
            width, height = analysis.get("image_size", (0, 0))
            summary_parts.append(f"Screen size: {width}x{height}")
            
            # UI elements
            ui_count = len(analysis.get("ui_elements", []))
            summary_parts.append(f"UI elements detected: {ui_count}")
            
            # Text elements
            text_count = len(analysis.get("text", []))
            summary_parts.append(f"Text elements: {text_count}")
            
            # Objects
            obj_count = len(analysis.get("objects", []))
            if obj_count > 0:
                summary_parts.append(f"Objects detected: {obj_count}")
            
            # Layout
            layout = analysis.get("layout", {})
            layout_type = layout.get("type", "unknown")
            summary_parts.append(f"Layout type: {layout_type}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Screen summary failed: {e}")
            return f"Failed to generate summary: {e}"


# Example usage and testing
if __name__ == "__main__":
    # Test the Vision Agent
    vision = VisionAgent()
    
    # Test with a sample image (if available)
    test_image = "test_screenshot.png"
    if os.path.exists(test_image):
        analysis = vision.analyze_screen(test_image)
        print("Screen Analysis:")
        print(json.dumps(analysis, indent=2))
        
        summary = vision.get_screen_summary(test_image)
        print("\nScreen Summary:")
        print(summary)
    else:
        print("No test image found. Place a screenshot named 'test_screenshot.png' to test.")









