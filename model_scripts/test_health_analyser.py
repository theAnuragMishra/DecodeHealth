import os
import argparse
from PIL import Image
from datetime import datetime
import json
from health_report_visualizer import generate_health_summary, generate_health_visualization

# Sample health reports for testing
SAMPLE_REPORTS = {
    "cardiac": """
    Patient presents with elevated cardiac enzymes and ST-segment elevation on ECG.
    History of hypertension and smoking. Echocardiogram shows reduced ejection fraction (35%).
    Recommended urgent cardiac catheterization.
    """,
    
}

def test_analysis_and_visualization(report_text, llm_api_choice, output_dir="test_output"):
    """Run full test pipeline for a given report text"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Test analysis
        print("\n" + "="*40)
        print("Testing health analysis...")
        annotated_report, vulnerabilities = generate_health_summary(report_text, llm_api_choice)
        
        print("\nIdentified Vulnerabilities:")
        print(json.dumps(vulnerabilities, indent=2))
        
        print("\nAnnotated Report:")
        print(annotated_report)
        
        # Save annotated report
        report_path = os.path.join(output_dir, f"report_{timestamp}.txt")
        with open(report_path, "w") as f:
            f.write(annotated_report)
        print(f"\nSaved report to {report_path}")
        
        # Test visualization
        print("\n" + "="*40)
        print("Testing visualization...")
        img = generate_health_visualization(
            vulnerabilities,
            gender="male",
            crazy_mode=True
        )
        
        # Save visualization
        img_path = os.path.join(output_dir, f"visualization_{timestamp}.png")
        img.save(img_path)
        print(f"Saved visualization to {img_path}")
        
        # Display the image
        img.show()
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise

def run_full_test_suite(llm_api_choice="ollama", output_dir="test_output"):
    """Test with all sample reports"""
    for case_name, report_text in SAMPLE_REPORTS.items():
        print(f"\n{'#'*20} Testing {case_name} case {'#'*20}")
        test_analysis_and_visualization(report_text, llm_api_choice, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Health Report Analyzer")
    parser.add_argument("--api", choices=["ollama", "huggingface", "together", "localai"],
                       default="ollama", help="Choose LLM API to test")
    parser.add_argument("--output-dir", default="test_output",
                       help="Output directory for test results")
    args = parser.parse_args()

    print(f"Running tests with {args.api} API...")
    run_full_test_suite(llm_api_choice=args.api, output_dir=args.output_dir)
    print("\nAll tests completed!")