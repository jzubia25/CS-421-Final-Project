
function loadContent(option) {
  const user_id = document.querySelector('.user-data').getAttribute('value');
  console.log(user_id);
  console.log(option);
  let user_url = `/${option}/${user_id}`;
  console.log(user_url);
  fetch(user_url)
    .then(response => response.json())
    .then(data => {
      const artworkContainer = document.querySelector('.artwork-grid');
      while (artworkContainer.firstChild) {
        artworkContainer.removeChild(artworkContainer.firstChild);
      }
      //Create items
      for (let key in data) {
        createThumbnail(data[key], artworkContainer)
      }
    });
}

function createThumbnail(item, container) {
  const card = document.createElement('div');
  card.classList.add('artwork-thumbnail')

  //change to details page
  let artworkDetailsPage = `/artwork/${item.id}`;
  const link = document.createElement('a');
  link.href = artworkDetailsPage;
  card.appendChild(link)

  const img = document.createElement('img');
  img.src = item.url;
  link.appendChild(img)

  const title = document.createElement('div');
  title.classList.add('art-title');
  card.appendChild(title);

  const titleP = document.createElement('p');
  titleP.textContent = item.title
  title.appendChild(titleP);

  container.appendChild(card);
}