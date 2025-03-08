document.addEventListener("DOMContentLoaded", () => {
  const skills = [
      { name: "HTML", level: 90 },
      { name: "CSS", level: 85 },
      { name: "JavaScript", level: 25 },
      { name: "Django", level: 70 },
      { name: "Python", level: 92 },
      { name: "Machine Learning", level: 75 },
      { name: "Deep Learning", level: 65 },
  ];

  const skillsContainer = document.getElementById("skills-container");
  
  if (!skillsContainer) return;

  // Clear existing content
  skillsContainer.innerHTML = "";

  skills.forEach((skill) => {
      const skillCard = document.createElement("div");
      skillCard.className = "bg-white rounded-lg shadow-md p-4 mb-4";
      skillCard.innerHTML = `
          <div class="flex justify-between mb-2">
              <h3 class="font-medium">${skill.name}</h3>
              <span class="text-gray-500">${skill.level}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5">
              <div class="skill-bar bg-blue-600 h-2.5 rounded-full" 
                   data-width="${skill.level}" 
                   style="width: 0%;">
              </div>
          </div>
      `;
      skillsContainer.appendChild(skillCard);
  });

  // Using IntersectionObserver for animating skill bars
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const bars = entry.target.querySelectorAll(".skill-bar");
          bars.forEach(bar => {
            const width = bar.getAttribute("data-width");
            bar.style.transition = "width 1.5s ease-out";
            bar.style.width = `${width}%`;
          });
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );

  observer.observe(skillsContainer);
});