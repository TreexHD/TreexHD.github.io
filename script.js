const username = 'TreexHD';
const repoList = document.querySelector('.repo-list');

fetch(`https://api.github.com/users/${username}/repos?sort=updated`)
  .then(res => res.json())
  .then(data => {
    data.forEach(repo => {
      const li = document.createElement('li');
      li.innerHTML = `
        <a class="repo-name" href="${repo.html_url}" target="_blank" rel="noopener">${repo.name}</a>
        ${repo.description ? `<p class="repo-desc">${repo.description}</p>` : ''}
      `;
      repoList.appendChild(li);
    });
  })
  .catch(err => console.error('Error fetching repos:', err));
