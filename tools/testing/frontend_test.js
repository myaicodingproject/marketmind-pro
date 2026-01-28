// MarketMind Pro - Frontend Functionality Test
// Copy and paste this into your browser console (F12) to test all functionality

console.log("🧪 Testing MarketMind Pro Frontend Functionality");
console.log("=" * 50);

// Test 1: Check if functions exist
console.log("1. Testing function availability:");
console.log("   downloadReport function:", typeof downloadReport);
console.log("   viewFullReport function:", typeof viewFullReport);
console.log("   searchCompany function:", typeof searchCompany);
console.log("   loadSystemStatus function:", typeof loadSystemStatus);

// Test 2: Test API endpoints
console.log("\n2. Testing API endpoints:");

// Test company search
fetch('/api/v1/companies/search?q=AAPL')
  .then(r => r.json())
  .then(data => console.log("   ✅ Company Search API:", data))
  .catch(e => console.log("   ❌ Company Search API:", e));

// Test system status
fetch('/api/system/status')
  .then(r => r.json())
  .then(data => console.log("   ✅ System Status API:", data))
  .catch(e => console.log("   ❌ System Status API:", e));

// Test 3: Test button functionality
console.log("\n3. Testing button functions:");
try {
  console.log("   Testing downloadReport('test-123'):");
  // This should show an alert
  downloadReport('test-123');
  console.log("   ✅ downloadReport function works");
} catch (e) {
  console.log("   ❌ downloadReport function failed:", e);
}

try {
  console.log("   Testing viewFullReport('test-123'):");
  // This should show an alert
  viewFullReport('test-123');
  console.log("   ✅ viewFullReport function works");
} catch (e) {
  console.log("   ❌ viewFullReport function failed:", e);
}

// Test 4: Simulate full workflow
console.log("\n4. Testing full workflow:");
console.log("   Simulating search for AAPL...");

// Set search input
document.getElementById('searchInput').value = 'AAPL';

// Trigger search
searchCompany().then(() => {
  console.log("   ✅ Search completed");
  
  // Wait a bit then try to find generate button
  setTimeout(() => {
    const generateButton = document.querySelector('button[onclick*="generateReport"]');
    if (generateButton) {
      console.log("   ✅ Generate Report button found");
      console.log("   Click the Generate Report button to test full workflow");
    } else {
      console.log("   ❌ Generate Report button not found");
    }
  }, 1000);
}).catch(e => {
  console.log("   ❌ Search failed:", e);
});

console.log("\n🎯 Test completed! Check the results above.");
console.log("If you see any ❌ errors, there are issues to fix.");
console.log("If all show ✅, everything is working correctly!");
