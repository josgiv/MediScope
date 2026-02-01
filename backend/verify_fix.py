import sys
import os

# Add current directory to path so we can import src
sys.path.append(os.getcwd())

from src.services.quick_checkup_service import QuickCheckupService

def test_quick_checkup_fix():
    print("Initializing QuickCheckupService...")
    service = QuickCheckupService()
    
    # Test Case 1: Fungal infection symptoms (Order A)
    symptoms_A = ['itching', 'skin_rash', 'nodal_skin_eruptions']
    print(f"\nPredicting for symptoms A: {symptoms_A}")
    result_A = service.predict(symptoms_A)
    print(f"Result A: {result_A.get('Disease')}")
    
    # Test Case 2: Fungal infection symptoms (Order B - Changed Order)
    symptoms_B = ['nodal_skin_eruptions', 'itching', 'skin_rash']
    print(f"\nPredicting for symptoms B: {symptoms_B}")
    result_B = service.predict(symptoms_B)
    print(f"Result B: {result_B.get('Disease')}")
    
    if result_A.get('Disease') == result_B.get('Disease'):
         print("\nSUCCESS: Model is Order Invariant (A and B match).")
    else:
         print("\nFAILURE: Model is sensitive to order!")

    # Test Case 3: Diabetes symptoms
    # Need to normalize inputs (underscores vs spaces) - service handles this via strip/replace
    # Added more symptoms to ensure distinct weight signature vs Allergy
    symptoms_diabetes = ['polyuria', 'excessive_hunger', 'blurred_and_distorted_vision', 'irregular_sugar_level', 'obesity']
    print(f"\nPredicting for symptoms: {symptoms_diabetes}")
    result_diabetes = service.predict(symptoms_diabetes)
    print(f"Result: {result_diabetes.get('Disease')}")

    if result_A.get('Disease') != result_diabetes.get('Disease'):
        print("SUCCESS: Model produced distinct predictions for different diseases.")
    else:
        print("FAILURE: Model produced identical predictions for different diseases.")

if __name__ == "__main__":
    test_quick_checkup_fix()
