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
import paste

from paste import HealthReportAnalyzer, HealthVisualizer, generate_health_summary, generate_health_visualization

def test_health_analyzer(llm_api_choice="ollama", should_save_files=True):
    """
    Test the HealthReportAnalyzer and HealthVisualizer classes
    
    Args:
        llm_api_choice: Which LLM API to use ("ollama", "huggingface", "together", "localai")
        should_save_files: Whether to save output files
    """
    print(f"Testing HealthReportAnalyzer with {llm_api_choice} API")
    
    # Sample health report text
    report_text = """
    Patient Health Summary:
    
    47-year-old male with history of hypertension and elevated cholesterol. Blood pressure 
    measured today at 145/95, which is concerning. Recent lab work shows LDL at 155 mg/dL, 
    suggesting increased cardiovascular risk. Complains of occasional chest pain after exercise.
    
    Lungs show mild wheezing indicative of potential early-stage COPD, likely related to 
    15-year smoking history. Patient reports chronic cough in mornings.
    
    Liver enzymes (ALT, AST) slightly elevated, suggesting mild hepatic strain, possibly 
    related to reported alcohol consumption (2-3 drinks daily).
    
    Right knee pain persists from old sports injury, showing moderate joint degeneration on 
    X-ray. Left shoulder exhibits limited range of motion with pain at extremes.
    
    Family history includes father with MI at 50 and mother with type 2 diabetes.
    
    Recommendations include cardiac stress test, smoking cessation program, and liver 
    function monitoring.
    """
    
    # Create output directory if it doesn't exist
    if should_save_files and not os.path.exists("output"):
        os.makedirs("output")
    
    # Option 1: Use the analyzer and visualizer classes directly
    try:
        print("\nTesting individual components:")
        # Initialize analyzer
        analyzer = HealthReportAnalyzer(llm_api_choice)
        
        # Analyze report
        print("Analyzing report...")
        vulnerabilities = analyzer.analyze_report(report_text)
        print(f"Identified vulnerabilities: {json.dumps(vulnerabilities, indent=2)}")
        
        # Generate annotated report
        print("Generating annotated report...")
        annotated_report = analyzer.generate_annotated_report(report_text, vulnerabilities)
        print(f"Annotated report excerpt: {annotated_report[:200]}...")
        
        # Initialize visualizer
        visualizer = HealthVisualizer()
        
        # Generate visualizations with different options
        print("Generating visualizations...")
        img_normal = visualizer.generate_visualization(vulnerabilities, gender="male", crazy_mode=False)
        img_crazy = visualizer.generate_visualization(vulnerabilities, gender="male", crazy_mode=True)
        
        # Save outputs if requested
        if should_save_files:
            with open("output/vulnerabilities.json", "w") as f:
                json.dump(vulnerabilities, f, indent=2)
                
            with open("output/annotated_report.md", "w") as f:
                f.write(annotated_report)
                
            img_normal.save("output/visualization_normal.png")
            img_crazy.save("output/visualization_crazy.png")
            print("Files saved to 'output' directory")
    
    except Exception as e:
        print(f"Error in direct testing: {str(e)}")
    
    # Option 2: Use the convenience functions
    try:
        print("\nTesting convenience functions:")
        annotated_report, vulnerabilities = generate_health_summary(report_text, llm_api_choice)
        print(f"Generated summary with {len(vulnerabilities)} vulnerabilities")
        
        img = generate_health_visualization(vulnerabilities, gender="male", crazy_mode=True)
        
        if should_save_files:
            with open("output/summary_annotated_report.md", "w") as f:
                f.write(annotated_report)
                
            img.save("output/summary_visualization.png")
            print("Summary files saved to 'output' directory")
    
    except Exception as e:
        print(f"Error in convenience function testing: {str(e)}")
    
    print("\nTest complete!")

def test_fallback_functionality():
    """Test the fallback functionality when LLM API is not available"""
    print("\nTesting fallback functionality (simulated API failure)...")
    
    # Create an analyzer with an invalid API choice to force fallback
    analyzer = HealthReportAnalyzer("invalid_api")
    
    # Sample report text
    report_text = """
    Patient has high blood pressure (170/95) and complains of chest pain.
    Lab results show elevated glucose levels indicating potential diabetes.
    Brain MRI shows no abnormalities. Knee pain persists from old injury.
    """
    
    try:
        # This should fall back to basic text analysis
        print("Attempting to analyze with invalid API...")
        vulnerabilities = analyzer.analyze_report(report_text)
        print(f"Fallback analysis result: {json.dumps(vulnerabilities, indent=2)}")
        
        # Visualize the results
        visualizer = HealthVisualizer()
        img = visualizer.generate_visualization(vulnerabilities, crazy_mode=False)
        
        if not os.path.exists("output"):
            os.makedirs("output")
        img.save("output/fallback_visualization.png")
        print("Fallback visualization saved to 'output/fallback_visualization.png'")
        
    except Exception as e:
        print(f"Error in fallback testing: {str(e)}")

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        llm_api = sys.argv[1]
    else:
        # Default to using Ollama if no argument provided
        llm_api = "ollama"
    
    # Run tests
    test_health_analyzer(llm_api_choice=llm_api)
    test_fallback_functionality()