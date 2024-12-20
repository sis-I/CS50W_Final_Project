// Get CSRFToken from Cookie
const csrfToken = getCookieValue('csrftoken');

async function toggleFollow(followBtns, followerCounts = null) {
  // New array of buttons
  let followButtons = followBtns.length > 0 ? followBtns : [followBtns];

  // Get button's text 
  let action = followButtons[0].innerText.toLowerCase();

  // Get username from dataset username
  let username = followButtons[0].dataset.username;

  // Fetch api
  try {

    const response = await fetch(`/follow/${username}`, {
                                  method: 'POST',
                                  headers: {
                                    'X-CSRFToken': csrfToken,
                                    'Content-Type': 'application/json',
                                  },
                                  body: JSON.stringify({ action }),
                                });

    const data = await response.json();

    if (data.error) return; // Exit if error has occured
  
    followButtons.forEach(button => {
      updateFollowBtnContent(button, action)
    });

    // update follower count
    if (followerCounts) {
      followCountUpdate(followerCounts, action);
    }

  } catch (error) {
    console.log(error);
  }

}

// Count Update helper function
function followCountUpdate(followerCounts, action) {
  // Array of count elements for the same type of element in a page
  let countElements = followerCounts.length > 0 ? followerCounts : [followerCounts];

  countElements.forEach(countElement => {
    let prevCount = parseInt(countElement.innerText);
    countElement.innerHTML = action === 'follow' ? prevCount + 1 : prevCount - 1;
  });
}

// Update follow button content helper function
function updateFollowBtnContent(button, action) {
  button.innerHTML = action === 'follow' ? 'Unfollow' : 'Follow';
}


// Fetching Toggle Api
async function fetchNToggle(params) {
  const { btns, url, method, iconName, like_on } = params;
  let buttonsToToggle = btns.length > 0 ? btns : [btns]; // For same button 

  let action = buttonsToToggle[0].dataset.action;

  try {
    const resp = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'appliction/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({
        action: action,
      }),
    });
  
    const data = await resp.json();
    if (!data.success) return; // Exit if not success response
      
    // Go on with toggling of a button
    buttonsToToggle.forEach(b => {
      if (iconName === 'bookmark') {
        toggleBookmark(b)
      } else if (iconName === 'like') {
        toggleLike(b, like_on);
      }
    });
    
  } catch(error) {
    console.log(error);
  }
}

// Function for toggling Like 
function toggleLike(btn, like_on) {
  const icon = btn.querySelector('i');
  let action = btn.dataset.action;

  // Update like counts
  const likeCountSpan = btn.querySelector(`.${like_on}_total-likes`);
  likeCountUpdate(likeCountSpan, action);

  // Toggle like button
  likeIconToggle(icon, action);

  // Change action dataset
  toggleLikeBtnAction(btn, action);
}

// Count Update helper function
function likeCountUpdate(countSpan, action) {
  let prevLikeCount = parseInt(countSpan.innerText);
  countSpan.innerText = action == 'like' ? prevLikeCount + 1 : prevLikeCount - 1;
}

// Like icon toggling helper function
function likeIconToggle(icon, action) {
  let iconClassName = 'bi-hand-thumbs-up';
  let isLiking = action == 'like';

  // Toggle like icon
  icon.classList.toggle(`${iconClassName}-fill`, isLiking);
  icon.classList.toggle(iconClassName, !isLiking);

}

// Update like button action dataset 
function toggleLikeBtnAction(btn, action) {
  btn.dataset.action = action === 'like' ? 'unlike' : 'like';

}

// Toggle bookmark icon function
function toggleBookmark(bookmarkBtn) {
  const icon = bookmarkBtn.querySelector('i');
  let iconClassName = 'bi-bookmark-';
  let action = bookmarkBtn.dataset.action;

  let isBookmarking = action == 'bookmark';

  // Toggle bookmark button icon
  icon.classList.toggle(`${iconClassName}fill`, isBookmarking)
  icon.classList.toggle(`${iconClassName}plus`, !isBookmarking)

  bookmarkBtn.title = action === 'bookmark' ? 'Delete from bookmark' : 'Save to bookmark';
  bookmarkBtn.dataset.action = action === 'bookmark' ? 'unbookmark' : 'bookmark';
}

// Get Estimated Read Minutes
const readMinutes = (content) => {
  let words = content.match(/\w+/g);

  if (!words) { return 0; }

  let readmin = Math.round(words.length / 250);
  return readmin < 1 ? 1 : readmin;
}

// Get Cookie Value [will be used to get csrftoken value]
function getCookieValue(name) {

  const cookieValue = document.cookie
    .split('; ')
    .find(cookie => cookie.startsWith(name + '='))
    ?.trim().split('=')[1];

  return cookieValue ? cookieValue : "";
}