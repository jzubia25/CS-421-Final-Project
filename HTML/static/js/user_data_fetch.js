
function loadContent(option) {
  const user_id = document.querySelector('.user-data').getAttribute('value');
  console.log(user_id);
  console.log(option);
  let user_url = `/${option}/${user_id}`;
  console.log(user_url);
  fetch(user_url)
    .then(response => response.json())
    .then(data => {
      console.log(data);
      const artworkContainer = document.querySelector('.artwork-grid');
      while (artworkContainer.firstChild) {
        artworkContainer.removeChild(artworkContainer.firstChild);
      }
      //Create items
      for (let key in data) {
        createThumbnail(option, data[key], artworkContainer);
        console.log(data[key]);
      }
    });
}

function createThumbnail(option, item, container) {
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

  const titleLink = document.createElement('a');
  titleLink.textContent = item.title
  titleLink.href = artworkDetailsPage;
  title.appendChild(titleLink);

  const price = document.createElement('p');
  price.textContent = `$${item.price.toFixed(2)}`;
  console.log(option)
  if (option == 'shop') {
    title.appendChild(price);
  }

  container.appendChild(card);
}

function loadExploreContent(category) {
  console.log(category);
  let user_url = `/category/${category}`;
  console.log(user_url);
  fetch(user_url)
    .then(response => response.json())
    .then(data => {
      const artworkContainer = document.querySelector('.artwork-grid');
      while (artworkContainer.firstChild) {
        artworkContainer.removeChild(artworkContainer.firstChild);
      }
      console.log(data);
      //Create items
      for (let key in data) {
        createExploreThumbnail(data[key], artworkContainer);
        console.log(data[key]);

      }
    });
}

function createExploreThumbnail(item, container) {
  const card = document.createElement('div');
  card.classList.add('artwork-thumbnail')
  console.log(item)
  console.log(item.id)
  //change to details page
  let artworkDetailsPage = `/artwork/${item.id}`;
  const link = document.createElement('a');
  link.href = artworkDetailsPage;
  card.appendChild(link)

  const img = document.createElement('img');
  img.src = item.url;
  link.appendChild(img)

  const details = document.createElement('div');
  card.classList.add('artwork-details')
  card.appendChild(details);

  const titleP = document.createElement('p');
  details.appendChild(titleP);


  const titleLink = document.createElement('a');
  titleLink.href = artworkDetailsPage;
  titleLink.textContent = item.title;
  titleP.appendChild(titleLink);

  const by = document.createTextNode(' by ')
  titleP.appendChild(by);

  let userPage = `/user/${item.user_id}`
  const userLink = document.createElement('a');
  userLink.href = userPage;
  userLink.textContent = `${item.artist}`
  titleP.appendChild(userLink);

  container.appendChild(card);
}