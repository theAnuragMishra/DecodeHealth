
import sys
import re
import random
import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
import spacy

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.call("python -m spacy download en_core_web_sm", shell=True)
    nlp = spacy.load("en_core_web_sm")

class HealthReportAnalyzer:
    """Uses an open-source LLM to analyze health reports and extract vulnerabilities"""

     def __init__(self, llm_api_choice="ollama"):
        """
        Initialize with choice of free/open-source LLM API
        Options:
        - "ollama": Local Ollama API (needs Ollama installed)
        - "huggingface": HuggingFace Inference API (needs API key)
        - "together": Together.ai API (needs API key)
        - "openai": OpenAI compatible endpoint for open models (e.g., LocalAI)
        """
        self.llm_api_choice = llm_api_choice
        self.setup_llm_api()

     def setup_llm_api(self):
      """Setup the chosen LLM API"""
      if self.llm_api_choice == "ollama":
        # Default Ollama endpoint, typically running locally
        self.api_endpoint = "http://localhost:11434/api/generate"
        self.model = "llama3" # Can be changed to any model available in Ollama
        print(f"Using Ollama with model '{self.model}' at {self.api_endpoint}")
        # Check if Ollama is installed and running
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                print(f"Available Ollama models: {', '.join([model['name'] for model in response.json()['models']])}")
            else:
                print("Ollama server appears to be running but didn't return model list")
        except:
            print("Warning: Couldn't connect to Ollama server. Make sure it's installed and running.")

      elif self.llm_api_choice == "huggingface":
        # Using HuggingFace Inference API
        self.api_endpoint = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.api_key = os.environ.get("HUGGINGFACE_API_KEY", HUGGINGFACE_API_KEY)
        if not self.api_key:
            print("Warning: HUGGINGFACE_API_KEY not found in environment variables")
            print("You can get a free API key at https://huggingface.co/settings/tokens")

      elif self.llm_api_choice == "together":
        # Using Together.ai API
        self.api_endpoint = "https://api.together.xyz/v1/completions"
        self.model = "mistralai/Mistral-7B-Instruct-v0.2"
        self.api_key = os.environ.get("TOGETHER_API_KEY", TOGETHER_API_KEY)
        if not self.api_key:
            print("Warning: TOGETHER_API_KEY not found in environment variables")

      elif self.llm_api_choice == "localai":
        # Using LocalAI for running open source models locally
        self.api_endpoint = os.environ.get("LOCALAI_API", "http://localhost:8080/v1/chat/completions")
        self.model = "phi3"  # Model depends on your LocalAI setup
        print(f"Using LocalAI with model '{self.model}' at {self.api_endpoint}")
        print("Make sure LocalAI is running with your desired model loaded")

      else:
        raise ValueError(f"Unsupported LLM API choice: {self.llm_api_choice}")

     def analyze_report(self, report_text):
        """
        Analyze the health report using the LLM to identify body parts and risk levels
        Returns a dictionary of {body_part: risk_level}
        """
        prompt = f"""
        Please analyze the following health report and identify which body parts are at risk
        and the corresponding risk level for each. Format your response as a JSON dictionary
        with body parts as keys and risk levels as values.

        Available risk levels (from highest to lowest): critical, severe, high, elevated, moderate, mild, low

        Example of desired output format:
        {{
            "heart": "high",
            "lungs": "moderate",
            "kidneys": "severe"
        }}

        Only include body parts that are explicitly mentioned or clearly implied in the report.
        Only output the JSON dictionary, nothing else.

        Health Report:
        {report_text}
        """

        response = self._call_llm_api(prompt)
        return self._parse_llm_response(response)

     def generate_annotated_report(self, report_text, vulnerabilities):
        """
        Generate an annotated version of the report with highlighted vulnerabilities
        """
        prompt = f"""
        Please reformat the following health report to highlight the identified vulnerabilities.
        For each vulnerability, add a brief explanation of the risk and potential preventive measures.

        Format your response as a clear, professional health risk assessment with sections.
        Add a "Recommendations" section at the end with personalized advice.

        Original Report:
        {report_text}

        Identified Vulnerabilities (body part: risk level):
        {json.dumps(vulnerabilities, indent=2)}
        """

        annotated_report = self._call_llm_api(prompt)
        return annotated_report

     def _call_llm_api(self, prompt):
      """Make API call to the selected LLM service"""
      try:
        if self.llm_api_choice == "ollama":
            # Ollama API request
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.api_endpoint, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json().get("response", "")

        elif self.llm_api_choice == "huggingface":
            # HuggingFace API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 500}}
            response = requests.post(self.api_endpoint, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()[0].get("generated_text", "")

        elif self.llm_api_choice == "together":
            # Together.ai API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "prompt": f"<s>[INST] {prompt} [/INST]",
                "max_tokens": 500,
                "temperature": 0.1
            }
            response = requests.post(self.api_endpoint, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json().get("choices", [{}])[0].get("text", "")

        elif self.llm_api_choice == "localai":
            # LocalAI API request (OpenAI compatible format)
            headers = {"Content-Type": "application/json"}

            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            response = requests.post(self.api_endpoint, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

        # If we get here, something went wrong
        print(f"Error: API call failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        return self._fallback_analysis(prompt)

      except Exception as e:
        print(f"Error calling LLM API: {str(e)}")
        # Fallback to basic text analysis if LLM API fails
        return self._fallback_analysis(prompt)

     def _parse_llm_response(self, response):
        """Parse the LLM response to extract the JSON dictionary"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'({.*?})', response.replace('\n', ' '), re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            else:
                # If no JSON found, see if the response is directly valid JSON
                return json.loads(response)
        except json.JSONDecodeError:
            print("Failed to parse LLM response as JSON. Using fallback extraction method.")
            # Fallback to regex extraction
            body_parts = {}
            risk_levels = ["critical", "severe", "high", "elevated", "moderate", "mild", "low"]

            for risk in risk_levels:
                # Look for patterns like "heart: high" or "heart - high"
                matches = re.finditer(r'(\w+)[\s:]*(' + risk + r')', response.lower())
                for match in matches:
                    body_part = match.group(1).strip()
                    if body_part not in ['risk', 'level']:  # Filter out false positives
                        body_parts[body_part] = risk

            if not body_parts:
                print("Warning: Could not extract risk levels from LLM response.")
                print(f"Raw response: {response}")

            return body_parts

     def _fallback_analysis(self, prompt):
        """
        Simple fallback analysis if LLM API is unavailable
        Uses basic regex to extract body parts and risk levels
        """
        # Check if we're analyzing a report or generating an annotated report
        if "Please analyze the following health report" in prompt:
            report_text = prompt.split("Health Report:")[1].strip()
            result = {}

            # Define common body parts to look for
            body_parts = [
                "heart", "lung", "lungs", "brain", "kidney", "kidneys", "liver",
                "stomach", "intestine", "intestines", "spine", "back", "joint",
                "joints", "knee", "knees", "shoulder", "shoulders", "eye", "eyes",
                "ear", "ears", "skin", "blood", "bone", "bones", "head", "chest",
                "cardiovascular", "respiratory", "digestive", "nervous", "skeletal"
            ]

            # Define risk levels to look for
            risk_levels = ["critical", "severe", "high", "elevated", "moderate", "mild", "low"]

            # Look for body parts with risk levels in the text
            for part in body_parts:
                if part in report_text.lower():
                    # Search for a risk level in the same sentence as the body part
                    sentences = re.split(r'[.!?]', report_text.lower())
                    for sentence in sentences:
                        if part in sentence:
                            assigned_risk = "moderate"  # Default risk level
                            for risk in risk_levels:
                                if risk in sentence:
                                    assigned_risk = risk
                                    break
                            result[part] = assigned_risk
                            break

            return json.dumps(result)

        elif "Please reformat the following health report" in prompt:
            # For annotated report generation
            original_report = prompt.split("Original Report:")[1].split("Identified Vulnerabilities")[0].strip()

            # Try to extract vulnerabilities
            vulnerabilities = {}
            try:
                vulnerabilities_text = prompt.split("Identified Vulnerabilities (body part: risk level):")[1].strip()
                vulnerabilities = json.loads(vulnerabilities_text)
            except:
                pass

            # Create a basic annotated report
            annotated_report = "# Health Risk Assessment Report\n\n"
            annotated_report += "## Summary\n"
            annotated_report += original_report + "\n\n"

            annotated_report += "## Identified Vulnerabilities\n"
            for part, risk in vulnerabilities.items():
                annotated_report += f"- **{part.capitalize()}**: {risk.capitalize()} risk\n"

            annotated_report += "\n## Recommendations\n"
            annotated_report += "- Consult with your healthcare provider for a complete evaluation\n"
            annotated_report += "- Consider lifestyle modifications to address identified risks\n"
            annotated_report += "- Follow up with appropriate specialists for high-risk areas\n"

            return annotated_report

class HealthVisualizer:
    def __init__(self):
    # Dictionary mapping body parts to approximate locations on a muscular anatomy image
    # Format: (x_center_percentage, y_center_percentage, radius_percentage)
      self.body_parts = {
        "head": (0.5, 0.08, 0.08),
        "brain": (0.5, 0.06, 0.07),
        "eye": (0.45, 0.07, 0.02),  # Left eye
        "eyes": [(0.45, 0.07, 0.02), (0.55, 0.07, 0.02)],  # Both eyes
        "ear": (0.4, 0.08, 0.02),  # Left ear
        "ears": [(0.4, 0.08, 0.02), (0.6, 0.08, 0.02)],  # Both ears
        "nose": (0.5, 0.09, 0.02),
        "mouth": (0.5, 0.11, 0.02),
        "throat": (0.5, 0.15, 0.03),
        "neck": (0.5, 0.13, 0.04),
        "shoulder": (0.32, 0.18, 0.04),  # Left shoulder - adjusted for muscular anatomy
        "shoulders": [(0.32, 0.18, 0.04), (0.68, 0.18, 0.04)],  # Both shoulders - wider placement
        "chest": (0.5, 0.22, 0.12),  # Slightly higher and larger for pectoral muscles
        "heart": (0.54, 0.23, 0.06),  # Adjusted position
        "lung": (0.4, 0.23, 0.06),  # Left lung - adjusted position
        "lungs": [(0.4, 0.23, 0.06), (0.6, 0.23, 0.06)],  # Both lungs - adjusted
        "stomach": (0.5, 0.33, 0.06),
        "abdomen": (0.5, 0.35, 0.1),  # Adjusted for visible abdominal muscles
        "liver": (0.62, 0.29, 0.05),  # Adjusted position
        "kidney": (0.65, 0.36, 0.04),  # Right kidney
        "kidneys": [(0.35, 0.36, 0.04), (0.65, 0.36, 0.04)],  # Both kidneys
        "gallbladder": (0.58, 0.32, 0.03),
        "pancreas": (0.52, 0.34, 0.03),
        "intestine": (0.5, 0.41, 0.08),
        "intestines": (0.5, 0.41, 0.08),
        "colon": (0.5, 0.43, 0.08),
        "bladder": (0.5, 0.47, 0.04),
        "pelvis": (0.5, 0.47, 0.08),
        "hip": (0.4, 0.47, 0.05),  # Left hip - adjusted for muscle visibility
        "hips": [(0.4, 0.47, 0.05), (0.6, 0.47, 0.05)],  # Both hips
        "arm": (0.28, 0.3, 0.05),  # Left arm - larger for bicep/tricep visibility
        "arms": [(0.28, 0.3, 0.05), (0.72, 0.3, 0.05)],  # Both arms - larger
        "elbow": (0.23, 0.38, 0.03),  # Left elbow
        "elbows": [(0.23, 0.38, 0.03), (0.77, 0.38, 0.03)],  # Both elbows
        "wrist": (0.2, 0.45, 0.02),  # Left wrist
        "wrists": [(0.2, 0.45, 0.02), (0.8, 0.45, 0.02)],  # Both wrists
        "hand": (0.18, 0.48, 0.03),  # Left hand
        "hands": [(0.18, 0.48, 0.03), (0.82, 0.48, 0.03)],  # Both hands
        "leg": (0.42, 0.65, 0.06),  # Left leg - larger for quadriceps/hamstrings
        "legs": [(0.42, 0.65, 0.06), (0.58, 0.65, 0.06)],  # Both legs - larger
        "knee": (0.42, 0.75, 0.04),  # Left knee
        "knees": [(0.42, 0.75, 0.04), (0.58, 0.75, 0.04)],  # Both knees
        "ankle": (0.42, 0.9, 0.03),  # Left ankle
        "ankles": [(0.42, 0.9, 0.03), (0.58, 0.9, 0.03)],  # Both ankles
        "foot": (0.42, 0.95, 0.04),  # Left foot
        "feet": [(0.42, 0.95, 0.04), (0.58, 0.95, 0.04)],  # Both feet
        "spine": (0.5, 0.3, 0.04),
        "back": (0.5, 0.3, 0.12),  # Larger for better coverage of back muscles
        "joints": [(0.23, 0.38, 0.03), (0.77, 0.38, 0.03), (0.42, 0.75, 0.04), (0.58, 0.75, 0.04)],  # Major joints
        "skin": "full_body",
        "blood": "full_body",
        "bones": "skeleton",
        "bone": "skeleton",
        "skeletal": "skeleton",
        "cardiovascular": [(0.54, 0.23, 0.06), "vessels"],  # Heart and vessels
        "respiratory": [(0.5, 0.15, 0.03), (0.4, 0.23, 0.06), (0.6, 0.23, 0.06)],  # Throat and lungs
        "digestive": [(0.5, 0.33, 0.06), (0.5, 0.41, 0.08)],  # Stomach and intestines
        "urinary": [(0.35, 0.36, 0.04), (0.65, 0.36, 0.04), (0.5, 0.47, 0.04)],  # Kidneys and bladder
        "nervous": [(0.5, 0.06, 0.07), (0.5, 0.3, 0.04)],  # Brain and spine
        "immune": "full_body",
        "lymphatic": "full_body",
        "endocrine": [(0.5, 0.06, 0.07), (0.52, 0.34, 0.03), (0.54, 0.2, 0.04)],  # Various glands
        "reproductive": (0.5, 0.5, 0.06),
        # Muscle-specific locations for muscular anatomy image
        "biceps": [(0.28, 0.28, 0.04), (0.72, 0.28, 0.04)],
        "triceps": [(0.26, 0.3, 0.04), (0.74, 0.3, 0.04)],
        "deltoids": [(0.32, 0.19, 0.04), (0.68, 0.19, 0.04)],
        "pectorals": (0.5, 0.21, 0.1),
        "abdominals": (0.5, 0.32, 0.09),
        "quadriceps": [(0.42, 0.6, 0.05), (0.58, 0.6, 0.05)],
        "hamstrings": [(0.42, 0.68, 0.05), (0.58, 0.68, 0.05)],
        "calves": [(0.42, 0.82, 0.04), (0.58, 0.82, 0.04)],
        "glutes": (0.5, 0.48, 0.08),
        "trapezius": (0.5, 0.17, 0.08),
        "latissimus": [(0.4, 0.25, 0.06), (0.6, 0.25, 0.06)]
    }

    # Risk levels with darker colors (slightly darkened from original)
      self.risk_levels = {
        'critical': '#E50000',  # Darker Red
        'severe': '#E52200',    # Darker Orange-Red
        'high': '#E57300',      # Darker Orange
        'elevated': '#E5C000',  # Darker Gold
        'moderate': '#E5E500',  # Darker Yellow
        'mild': '#80D625',      # Darker Green-Yellow
        'low': '#00D600'        # Darker Green
    }

        # Create a psychedelic color map for the crazy visual effect
      colors = [(0, 'magenta'), (0.25, 'blue'), (0.5, 'green'),
                 (0.75, 'yellow'), (1, 'red')]
      self.psychedelic_cmap = LinearSegmentedColormap.from_list('psychedelic', colors)

     def get_base_body_image(self, gender="neutral"):
      """Get a base body image from local file or create a placeholder"""
      local_path = f"images/{gender}_body.png"

      if os.path.exists(local_path):
        try:
            # Load the image and ensure it has an alpha channel for overlay
            img = Image.open(local_path)
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            return img
        except Exception as e:
            print(f"Error loading {local_path}: {str(e)}")
            return self._create_placeholder_body()
      else:
        print(f"Local image {local_path} not found")
        return self._create_placeholder_body()

     def _create_placeholder_body(self, width=600, height=1000):
        """Create a basic placeholder body outline image"""
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        # Draw a simple body outline
        # Head
        draw.ellipse([(width*0.4, height*0.02), (width*0.6, height*0.14)],
                     outline=(0, 0, 0), width=2)

        # Body
        draw.ellipse([(width*0.4, height*0.14), (width*0.6, height*0.5)],
                     outline=(0, 0, 0), width=2)

        # Arms
        draw.line([(width*0.42, height*0.18), (width*0.25, height*0.4)],
                  fill=(0, 0, 0), width=2)  # Left arm
        draw.line([(width*0.58, height*0.18), (width*0.75, height*0.4)],
                  fill=(0, 0, 0), width=2)  # Right arm

        # Legs
        draw.line([(width*0.45, height*0.5), (width*0.4, height*0.9)],
                  fill=(0, 0, 0), width=2)  # Left leg
        draw.line([(width*0.55, height*0.5), (width*0.6, height*0.9)],
                  fill=(0, 0, 0), width=2)  # Right leg

        return image

     def generate_visualization(self, body_parts_risks, base_image=None, gender="neutral", crazy_mode=True):
        """
        Generate a visualization highlighting the body parts with associated risks

        Args:
            body_parts_risks: Dictionary of {body_part: risk_level}
            base_image: Optional PIL Image to use as the base image
            gender: "male", "female", or "neutral" for default image selection
            crazy_mode: Whether to apply psychedelic effects

        Returns:
            PIL Image object with highlighted body parts
        """
        # Get base body image if not provided
        if base_image is None:
            base_image = self.get_base_body_image(gender)

        # Create a transparent overlay for the highlights
        highlight_layer = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(highlight_layer)

        # Apply crazy psychedelic background if requested
        if crazy_mode:
            base_image = self._apply_psychedelic_background(base_image)

        # Highlight each affected body part
        for part, risk in body_parts_risks.items():
            self._highlight_body_part(draw, part, risk, base_image.width, base_image.height)

        # Overlay the highlights on the base image
        result_image = Image.alpha_composite(base_image, highlight_layer)

        # Add labels for the affected parts
        result_image = self._add_labels(result_image, body_parts_risks)

        # Add title and legend
        result_image = self._add_title_and_legend(result_image, body_parts_risks)

        return result_image

     def _apply_psychedelic_background(self, image):
        """Apply a crazy psychedelic effect to the image background"""
        # Create a new image with the same size
        width, height = image.size
        psychedelic_bg = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # Create psychedelic pattern
        data = np.zeros((height, width, 4), dtype=np.uint8)

        for y in range(height):
            for x in range(width):
                # Create trippy pattern with complex waves
                wave1 = np.sin(x/20 + y/30) * 0.5 + 0.5
                wave2 = np.cos(x/15 - y/25) * 0.5 + 0.5
                wave3 = np.sin((x+y)/40) * 0.5 + 0.5

                # Convert waves to RGB using our psychedelic colormap
                r, g, b = [int(255 * c) for c in self.psychedelic_cmap(wave1)[:3]]

                # Add animated-looking effect
                r = (r + int(255 * wave2)) % 256
                b = (b + int(255 * wave3)) % 256

                # Set pixel with some transparency
                data[y, x, 0] = r
                data[y, x, 1] = g
                data[y, x, 2] = b
                data[y, x, 3] = 100  # Semi-transparent

        # Convert numpy array to PIL Image
        psychedelic_bg = Image.fromarray(data, 'RGBA')

        # Blend with original image
        return Image.alpha_composite(psychedelic_bg, image)

     def _highlight_body_part(self, draw, part, risk_level, width, height):
        """Highlight a body part with the appropriate risk color"""
        color_hex = self.risk_levels.get(risk_level, '#FFFF00')  # Default to yellow if risk not found

        # Convert hex color to RGBA with transparency
        r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        color = (r, g, b, 150)  # Semi-transparent

        # Get the part location info
        part_info = self.body_parts.get(part)

        if part_info == "full_body":
            # Special case for full body highlight
            self._highlight_full_body(draw, color, width, height)
            return
        elif part_info == "skeleton":
            # Special case for skeleton
            self._highlight_skeleton(draw, color, width, height)
            return
        elif part_info == "vessels":
            # Special case for blood vessels
            self._highlight_vessels(draw, color, width, height)
            return
        elif isinstance(part_info, list):
            # Multiple locations (like both arms)
            for location in part_info:
                if isinstance(location, tuple):
                    x_center = width * location[0]
                    y_center = height * location[1]
                    radius = width * location[2]

                    # Add crazy effect with multiple concentric circles
                    for i in range(5):
                        radius_mod = radius * (1 + i*0.3)
                        alpha = min(150, 150 - i*30)  # Decreasing alpha for outer circles
                        glow_color = (r, g, b, alpha)

                        draw.ellipse([(x_center - radius_mod, y_center - radius_mod),
                                      (x_center + radius_mod, y_center + radius_mod)],
                                     fill=glow_color)
                else:
                    # Special section within the list
                    self._highlight_special_section(draw, color, location, width, height)
        elif isinstance(part_info, tuple):
            # Single location
            x_center = width * part_info[0]
            y_center = height * part_info[1]
            radius = width * part_info[2]

            # Create a "glowing" effect with multiple circles
            for i in range(5):
                radius_mod = radius * (1 + i*0.3)
                alpha = min(150, 150 - i*30)
                glow_color = (r, g, b, alpha)

                draw.ellipse([(x_center - radius_mod, y_center - radius_mod),
                            (x_center + radius_mod, y_center + radius_mod)],
                           fill=glow_color)

     def _highlight_full_body(self, draw, color, width, height):
        """Highlight the entire body with a glowing effect"""
        # Create a semi-transparent overlay for the whole body
        r, g, b, a = color
        overlay_color = (r, g, b, 80)  # Lower alpha for full body

        # Draw a full body silhouette with the glow
        body_shape = [
            # Head and neck
            (width*0.5, height*0.05),  # Top of head
            (width*0.4, height*0.08),  # Left side of head
            (width*0.35, height*0.15), # Neck left

            # Left arm and shoulder
            (width*0.3, height*0.2),   # Left shoulder
            (width*0.2, height*0.4),   # Left elbow
            (width*0.15, height*0.5),  # Left hand

            # Left side of torso and leg
            (width*0.25, height*0.5),  # Back to torso
            (width*0.35, height*0.6),  # Left hip
            (width*0.3, height*0.8),   #
                        (width*0.3, height*0.8),   # Left knee
            (width*0.3, height*0.95),  # Left foot

            # Right leg and foot
            (width*0.7, height*0.95),  # Right foot
            (width*0.7, height*0.8),   # Right knee

            # Right side of torso and arm
            (width*0.65, height*0.6),  # Right hip
            (width*0.75, height*0.5),  # Right hand
            (width*0.8, height*0.4),   # Right elbow
            (width*0.7, height*0.2),   # Right shoulder

            # Back to head
            (width*0.65, height*0.15), # Neck right
            (width*0.6, height*0.08),  # Right side of head
            (width*0.5, height*0.05),  # Back to top of head
        ]

        # Draw a filled body shape
        draw.polygon(body_shape, fill=overlay_color)

        # Add a glowing effect around the body
        for i in range(3):
            glow_alpha = 40 - (i * 10)
            if glow_alpha > 0:
                glow_color = (r, g, b, glow_alpha)
                draw.line(body_shape + [body_shape[0]], fill=glow_color, width=10+(i*5))

     def _highlight_skeleton(self, draw, color, width, height):
        """Highlight the skeleton with a glowing effect"""
        r, g, b, a = color
        bone_color = (r, g, b, 120)

        # Draw major bones with lines
        # Spine
        draw.line([(width*0.5, height*0.15), (width*0.5, height*0.5)],
                fill=bone_color, width=int(width*0.03))

        # Ribcage (simplified)
        for i in range(5):
            y_pos = height*(0.2 + i*0.05)
            draw.line([(width*0.4, y_pos), (width*0.6, y_pos)],
                    fill=bone_color, width=int(width*0.015))

        # Shoulder bones
        draw.line([(width*0.35, height*0.2), (width*0.65, height*0.2)],
                fill=bone_color, width=int(width*0.02))

        # Arms
        draw.line([(width*0.35, height*0.2), (width*0.2, height*0.4), (width*0.15, height*0.5)],
                fill=bone_color, width=int(width*0.02))  # Left arm
        draw.line([(width*0.65, height*0.2), (width*0.8, height*0.4), (width*0.85, height*0.5)],
                fill=bone_color, width=int(width*0.02))  # Right arm

        # Pelvis
        draw.arc([(width*0.4, height*0.45), (width*0.6, height*0.55)],
               start=0, end=180, fill=bone_color, width=int(width*0.02))

        # Legs
        draw.line([(width*0.4, height*0.5), (width*0.35, height*0.75), (width*0.35, height*0.95)],
                fill=bone_color, width=int(width*0.02))  # Left leg
        draw.line([(width*0.6, height*0.5), (width*0.65, height*0.75), (width*0.65, height*0.95)],
                fill=bone_color, width=int(width*0.02))  # Right leg

        # Skull (simplified)
        draw.ellipse([(width*0.43, height*0.05), (width*0.57, height*0.15)],
                   outline=bone_color, width=int(width*0.015))

        # Add a glow effect
        for i in range(3):
            glow_alpha = 50 - (i * 15)
            if glow_alpha > 0:
                glow_color = (r, g, b, glow_alpha)

                # Apply glow to all bone lines
                draw.line([(width*0.5, height*0.15), (width*0.5, height*0.5)],
                        fill=glow_color, width=int(width*0.03) + (i*4))

                for j in range(5):
                    y_pos = height*(0.2 + j*0.05)
                    draw.line([(width*0.4, y_pos), (width*0.6, y_pos)],
                            fill=glow_color, width=int(width*0.015) + (i*4))

                # More glow effects for other bones...

     def _highlight_vessels(self, draw, color, width, height):
        """Highlight blood vessels with a network of lines"""
        r, g, b, a = color
        vessel_color = (r, g, b, 100)

        # Draw major blood vessels branching from the heart
        heart_x, heart_y = width*0.55, height*0.25

        # Aorta and major arteries
        draw.line([(heart_x, heart_y), (heart_x, heart_y - height*0.05)],
                fill=vessel_color, width=int(width*0.015))

        # Branching to head
        draw.line([(heart_x, heart_y - height*0.05), (heart_x - width*0.05, height*0.15)],
                fill=vessel_color, width=int(width*0.01))
        draw.line([(heart_x, heart_y - height*0.05), (heart_x + width*0.05, height*0.15)],
                fill=vessel_color, width=int(width*0.01))

        # Continue to brain
        draw.line([(heart_x - width*0.05, height*0.15), (width*0.45, height*0.05)],
                fill=vessel_color, width=int(width*0.008))
        draw.line([(heart_x + width*0.05, height*0.15), (width*0.55, height*0.05)],
                fill=vessel_color, width=int(width*0.008))

        # Down the body
        draw.line([(heart_x, heart_y), (heart_x, height*0.5)],
                fill=vessel_color, width=int(width*0.012))

        # Split to legs
        draw.line([(heart_x, height*0.5), (width*0.4, height*0.75)],
                fill=vessel_color, width=int(width*0.01))
        draw.line([(heart_x, height*0.5), (width*0.6, height*0.75)],
                fill=vessel_color, width=int(width*0.01))

        # Continue to feet
        draw.line([(width*0.4, height*0.75), (width*0.35, height*0.95)],
                fill=vessel_color, width=int(width*0.008))
        draw.line([(width*0.6, height*0.75), (width*0.65, height*0.95)],
                fill=vessel_color, width=int(width*0.008))

        # To arms
        draw.line([(heart_x, heart_y), (width*0.3, height*0.3)],
                fill=vessel_color, width=int(width*0.01))
        draw.line([(heart_x, heart_y), (width*0.7, height*0.3)],
                fill=vessel_color, width=int(width*0.01))

        # Continue to hands
        draw.line([(width*0.3, height*0.3), (width*0.2, height*0.48)],
                fill=vessel_color, width=int(width*0.008))
        draw.line([(width*0.7, height*0.3), (width*0.8, height*0.48)],
                fill=vessel_color, width=int(width*0.008))

        # Add pulsing glow effect
        for i in range(3):
            glow_alpha = 40 - (i * 10)
            if glow_alpha > 0:
                glow_color = (r, g, b, glow_alpha)

                # Apply pulsing effect to major vessels
                draw.line([(heart_x, heart_y), (heart_x, heart_y - height*0.05)],
                        fill=glow_color, width=int(width*0.015) + (i*5))
                draw.line([(heart_x, heart_y), (heart_x, height*0.5)],
                        fill=glow_color, width=int(width*0.012) + (i*5))

     def _highlight_special_section(self, draw, color, section_name, width, height):
        """Highlight special sections like respiratory system, etc."""
        if section_name == "vessels":
            self._highlight_vessels(draw, color, width, height)
        # Add more special sections as needed

     def _add_labels(self, image, body_parts_risks):
      """Add text labels for the highlighted body parts with larger font and better positioning"""
      draw = ImageDraw.Draw(image)
      width, height = image.size

      # Increase font size significantly (from 0.02 to 0.03 of height)
      font_size = int(height * 0.03)

    # Try to load a font, fall back to default if not available
      try:
        font = ImageFont.truetype("arial.ttf", font_size)
      except IOError:
        try:
            # Try another common font if arial isn't available
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

    # Add labels for each body part
      for part, risk in body_parts_risks.items():
        part_info = self.body_parts.get(part)
        label_text = f"{part.capitalize()}: {risk.capitalize()}"

        # Get color for this risk level
        color_hex = self.risk_levels.get(risk, '#FFFF00')
        r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        text_color = (0, 0, 0)  # Black text

        if part_info == "full_body" or part_info == "skeleton" or part_info == "vessels":
            # Place label at top of image for full body highlights
            text_width = font_size * len(label_text) * 0.6
            x_pos = (width - text_width) / 2

            # Add a semi-transparent background for better readability
            text_size = draw.textbbox((0, 0), label_text, font=font)
            text_width = text_size[2] - text_size[0]
            text_height = text_size[3] - text_size[1]

            # Draw text background
            draw.rectangle([(x_pos - 5, height * 0.02 - 5),
                           (x_pos + text_width + 5, height * 0.02 + text_height + 5)],
                         fill=(255, 255, 255, 180))  # Semi-transparent white

            draw.text((x_pos, height * 0.02), label_text, fill=text_color, font=font)

        elif isinstance(part_info, list):
            # For multiple locations, choose the first concrete location
            for location in part_info:
                if isinstance(location, tuple):
                    x_center = width * location[0]
                    y_center = height * location[1]

                    # Better positioning with more space between highlight and text
                    x_offset = width * 0.1  # Increased offset
                    y_offset = height * 0.04  # Increased offset

                    text_pos = (x_center + x_offset, y_center - y_offset)

                    # Add text background
                    text_size = draw.textbbox((0, 0), label_text, font=font)
                    text_width = text_size[2] - text_size[0]
                    text_height = text_size[3] - text_size[1]

                    draw.rectangle([(text_pos[0] - 5, text_pos[1] - 5),
                                   (text_pos[0] + text_width + 5, text_pos[1] + text_height + 5)],
                                 fill=(255, 255, 255, 180))  # Semi-transparent white

                    draw.text(text_pos, label_text, fill=text_color, font=font)
                    break

        elif isinstance(part_info, tuple):
            x_center = width * part_info[0]
            y_center = height * part_info[1]
            radius = width * part_info[2]

            # Better positioning with more space
            x_offset = width * 0.1  # Increased offset
            y_offset = height * 0.04  # Increased offset

            text_pos = (x_center + x_offset, y_center - y_offset)

            # Add text background for better readability
            text_size = draw.textbbox((0, 0), label_text, font=font)
            text_width = text_size[2] - text_size[0]
            text_height = text_size[3] - text_size[1]

            draw.rectangle([(text_pos[0] - 5, text_pos[1] - 5),
                           (text_pos[0] + text_width + 5, text_pos[1] + text_height + 5)],
                         fill=(255, 255, 255, 180))  # Semi-transparent white

            draw.text(text_pos, label_text, fill=text_color, font=font)

      return image

     def _highlight_body_part(self, draw, part, risk_level, width, height):
      """Highlight a body part with the appropriate risk color"""
      color_hex = self.risk_levels.get(risk_level, '#FFFF00')  # Default to yellow if risk not found

    # Convert hex color to RGBA with increased opacity for darker effect
      r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    # Increase opacity from 150 to a darker 180
      color = (r, g, b, 180)  # Higher alpha for more opaque/darker effect

    # Get the part location info
      part_info = self.body_parts.get(part)

      if part_info == "full_body":
        # Special case for full body highlight
        self._highlight_full_body(draw, color, width, height)
        return
      elif part_info == "skeleton":
        # Special case for skeleton
        self._highlight_skeleton(draw, color, width, height)
        return
      elif part_info == "vessels":
        # Special case for blood vessels
        self._highlight_vessels(draw, color, width, height)
        return
      elif isinstance(part_info, list):
        # Multiple locations (like both arms)
        for location in part_info:
            if isinstance(location, tuple):
                x_center = width * location[0]
                y_center = height * location[1]
                radius = width * location[2]

                # Add fewer but darker circles for clearer highlighting
                for i in range(3):  # Reduced from 5 to 3 for cleaner look
                    radius_mod = radius * (1 + i*0.25)  # Smaller expansion for more precise highlighting
                    alpha = min(200, 200 - i*40)  # Higher starting alpha (200) for darker effect
                    glow_color = (r, g, b, alpha)

                    draw.ellipse([(x_center - radius_mod, y_center - radius_mod),
                                  (x_center + radius_mod, y_center + radius_mod)],
                                 fill=glow_color)
            else:
                # Special section within the list
                self._highlight_special_section(draw, color, location, width, height)
      elif isinstance(part_info, tuple):
        # Single location
        x_center = width * part_info[0]
        y_center = height * part_info[1]
        radius = width * part_info[2]

        # Create a "glowing" effect with multiple circles, but darker and more precise
        for i in range(3):  # Reduced from 5 to 3
            radius_mod = radius * (1 + i*0.25)  # More precise highlighting
            alpha = min(200, 200 - i*40)  # Darker effect with higher alpha
            glow_color = (r, g, b, alpha)

            draw.ellipse([(x_center - radius_mod, y_center - radius_mod),
                        (x_center + radius_mod, y_center + radius_mod)],
                       fill=glow_color)


     def _add_title_and_legend(self, image, body_parts_risks):
      """Add a title and risk level legend to the image with improved formatting"""
      # Create a new image with extra space for title and legend
      width, height = image.size
      new_height = height + int(height * 0.15)  # Extra 15% for title and legend
      new_image = Image.new('RGBA', (width, new_height), (255, 255, 255, 255))
      new_image.paste(image, (0, int(height * 0.1)))  # Add some padding at top

      draw = ImageDraw.Draw(new_image)

    # Increase font sizes for better readability
      try:
        title_font_size = int(height * 0.04)  # Increased from 0.03
        title_font = ImageFont.truetype("arial.ttf", title_font_size)
        legend_font_size = int(height * 0.03)  # Increased from 0.02
        legend_font = ImageFont.truetype("arial.ttf", legend_font_size)
      except IOError:
        try:
            # Try another common font
            title_font = ImageFont.truetype("DejaVuSans.ttf", title_font_size)
            legend_font = ImageFont.truetype("DejaVuSans.ttf", legend_font_size)
        except IOError:
            title_font = ImageFont.load_default()
            legend_font = ImageFont.load_default()

    # Add title with background for better visibility
      title = "Health Risk Visualization"

    # Calculate text width for centering
      text_size = draw.textbbox((0, 0), title, font=title_font)
      text_width = text_size[2] - text_size[0]
      text_height = text_size[3] - text_size[1]

      x_pos = (width - text_width) / 2
      y_pos = height * 0.03

    # Add title background
      draw.rectangle([(x_pos - 10, y_pos - 5),
                   (x_pos + text_width + 10, y_pos + text_height + 5)],
                 fill=(255, 255, 255, 220))  # Nearly opaque white

      draw.text((x_pos, y_pos), title, fill=(0, 0, 0), font=title_font)

    # Add legend with better formatting
      legend_x = width * 0.05
      legend_y = new_height - height * 0.05

    # Add legend background
      legend_bg_padding = 10
      legend_bg_height = height * 0.07  # Approximate legend height

      draw.rectangle([(legend_x - legend_bg_padding, legend_y - legend_bg_padding),
                   (width - legend_x + legend_bg_padding, legend_y + legend_bg_height)],
                 fill=(255, 255, 255, 200))  # Semi-transparent white

      draw.text((legend_x, legend_y), "Risk Levels:", fill=(0, 0, 0), font=legend_font)

    # Add color squares for each risk level that appears in the visualization
      risk_levels_found = set(body_parts_risks.values())

    # Sort by severity
      severity_order = ['critical', 'severe', 'high', 'elevated', 'moderate', 'mild', 'low']
      sorted_risks = [risk for risk in severity_order if risk in risk_levels_found]

    # Increase square size for better visibility
      square_size = int(height * 0.03)  # Increased from 0.02
      spacing = int(width * 0.12)  # Increased from 0.08 for more space between items

      for i, risk in enumerate(sorted_risks):
        color_hex = self.risk_levels.get(risk, '#FFFF00')
        r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

        # Draw color square - darker border for better definition
        x_pos = legend_x + spacing * i
        y_pos = legend_y + square_size + 5

        # Draw a black border around the color square
        draw.rectangle([(x_pos-1, y_pos-1), (x_pos + square_size+1, y_pos + square_size+1)],
                    fill=(0, 0, 0, 255))

        # Draw the color square
        draw.rectangle([(x_pos, y_pos), (x_pos + square_size, y_pos + square_size)],
                     fill=(r, g, b, 255))

        # Add risk level text
        draw.text((x_pos + square_size + 5, y_pos),
                 risk.capitalize(), fill=(0, 0, 0), font=legend_font)

      return new_image

def generate_health_summary(report_text, llm_api_choice="ollama"):
    """
    Generate annotated health summary from report text
    Returns tuple of (annotated_report, vulnerabilities_dict)
    """
    analyzer = HealthReportAnalyzer(llm_api_choice)
    vulnerabilities = analyzer.analyze_report(report_text)
    annotated_report = analyzer.generate_annotated_report(report_text, vulnerabilities)
    return annotated_report, vulnerabilities

def generate_health_visualization(vulnerabilities_dict, gender="neutral", crazy_mode=True):
    """
    Generate visualization image from vulnerabilities dictionary
    Returns PIL Image object
    """
    visualizer = HealthVisualizer()
    img = visualizer.generate_visualization(
        vulnerabilities_dict,
        gender=gender,
        crazy_mode=crazy_mode
    )
    return img