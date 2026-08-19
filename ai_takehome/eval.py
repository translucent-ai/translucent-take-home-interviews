from baseline_agent import answer
from semantic_agent import SemanticRetrievalAgent

tests = [
    ("Why are cardiology claims denied most often?", ["Cardiology", "Coding error"]),
    ("List common denial reasons for radiology.", ["Radiology", "Invalid", "Duplicate"]),
    ("Top duplicate claim issues?", ["Duplicate"]),
    ("Why do we have expired coverage denials?", ["Expired coverage"]),
    ("What missing info causes Pediatrics denials?", ["Pediatrics", "Missing"])
]

print("Evaluating Baseline Agent...")
passed = 0
for q, keywords in tests:
    ans = answer(q).lower()
    print("Baseline Agent Answer: ", ans)
    if all(k.lower() in ans for k in keywords):
        print("Passed")
        passed += 1
print(f"Score For Baseline Agent: {passed}/5")

print("Initializing Semantic Agent...")
semantic_agent = SemanticRetrievalAgent("data/denials.csv")
passed = 0
for q, keywords in tests:
    ans = semantic_agent.answer(q).lower()
    print("question: ", q)
    print("Answer: ", ans)
    if all(k.lower() in ans for k in keywords):
        print("Passed")
        passed += 1
print(f"Score For Semantic Agent: {passed}/5")