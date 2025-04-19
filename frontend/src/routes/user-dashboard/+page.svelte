<script lang="ts">
  import { onMount } from 'svelte';

  let user = {
    name: "Vaishnavi Tiwari",
    age: 40,
    email: "xyz104@example.com",
    profileImg: ""
  };

  let oldReports = [
    "Report A - Blood Test",
    "Report B - MRI",
    "Report C - ECG"
  ];

  let newReports = [
    {
      id: 1,
      title: "Liver Function Test",
      date: "2025-04-15",
      lab: "Lab A",
      viewOption: ""
    },
    {
      id: 2,
      title: "X-Ray Chest",
      date: "2025-04-10",
      lab: "Lab B",
      viewOption: ""
    }
  ];

  const submitReportOptions = () => {
    // console.log("Submitted view preferences:", newReports);
    // alert("Preferences submitted successfully!");

    newReports.forEach(report => {
      if (report.viewOption === 'voice') {
        const msg = `${report.title}, performed at ${report.lab} on ${report.date}`;
        const utterance = new SpeechSynthesisUtterance(msg);
        utterance.lang = 'en-US';
        speechSynthesis.speak(utterance);
      }
    });
  };

  const speakWelcome = () => {
    const msg = `Hello ${user.name}, here is your report summary. You have ${oldReports.length} old reports and ${newReports.length} new reports.`;
    const utterance = new SpeechSynthesisUtterance(msg);
    utterance.lang = 'en-US';
    speechSynthesis.speak(utterance);
  };

  onMount(() => {
    window.initializeGoogleTranslate = () => {
      new window.google.translate.TranslateElement({
        pageLanguage: 'en',
        includedLanguages: 'en,hi,bn,te,ta,mr,ml,kn,gu,pa,ur,or',
        layout: window.google.translate.TranslateElement.InlineLayout.SIMPLE
      }, 'google_translate_element');
    };

    const script = document.createElement('script');
    script.src = "https://translate.google.com/translate_a/element.js?cb=initializeGoogleTranslate";
    document.body.appendChild(script);
  });
</script>

<style>
  .speech-icon:hover {
    background-color: #f3f4f6;
  }
</style>

<div class="min-h-screen bg-gray-100 flex p-6 relative">
  <div class="absolute top-4 left-4 space-y-1 z-50">
    <p class="text-sm text-white bg-blue-900 rounded-full px-4 py-1 shadow">
      Change Language
    </p>
    <div id="google_translate_element" class="bg-white rounded-md p-1 shadow-md"></div>
  </div>

  <div class="absolute top-4 right-4 z-50">
    <button on:click={speakWelcome} class="bg-white p-2 rounded-full shadow speech-icon" title="Read Summary">
      <!-- Inline Speaker SVG Icon -->
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-800" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5L6 9H2v6h4l5 4V5z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.54 8.46a5 5 0 010 7.07M19.07 4.93a9 9 0 010 12.73" />
      </svg>
    </button>
  </div>

+  <div class="w-1/3 bg-white rounded-xl shadow-lg p-6 space-y-6">
    <div class="text-center">
      <img src={user.profileImg} alt="pic" class="w-24 h-24 rounded-full mx-auto mb-2" />
      <h2 class="text-xl font-semibold">{user.name}</h2>
      <p class="text-gray-600">Age: {user.age}</p>
      <p class="text-gray-600 text-sm">{user.email}</p>
    </div>

    <div>
      <h3 class="text-lg font-medium mb-2 border-b pb-1">Old Reports</h3>
      <ul class="list-disc list-inside space-y-1 text-gray-700">
        {#each oldReports as report}
          <li>{report}</li>
        {/each}
      </ul>
    </div>
  </div>

  <!-- Right Panel -->
  <div class="flex-1 ml-6 bg-white rounded-xl shadow-lg p-6">
    <h2 class="text-2xl font-semibold mb-6">Latest Report Updates</h2>

    <div class="space-y-6">
      {#each newReports as report}
        <div class="border border-gray-200 rounded-lg p-4 shadow-sm">
          <div class="mb-2">
            <h3 class="text-lg font-semibold">{report.title}</h3>
            <p class="text-gray-500 text-sm">Lab: {report.lab} | Date: {report.date}</p>
          </div>

          <div class="mt-3">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              View Report As:
              <select
                bind:value={report.viewOption}
                class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="" disabled selected>Select option</option>
                <option value="text">Text</option>
                <option value="voice">Voice</option>
              </select>
            </label>
          </div>
        </div>
      {/each}

      <div class="mt-6 text-right">
        <button
          on:click={submitReportOptions}
          class="bg-teal-600 text-white py-2 px-6 rounded-md hover:bg-teal-700 transition"
        >
          Submit Preferences
        </button>
      </div>
    </div>
  </div>
</div>
