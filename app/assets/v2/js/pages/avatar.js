var AvatarPage = (function(profileId) {

    var myAvatars;
    var presetAvatars;
    var myAvatarsInitialized = false;
    var presetAvatarsInitialized = false;
  
    function postSelection(url, avatarPk) {
      return fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ avatarPk: avatarPk })
      });
    }
  
    function updateNavAvatar(svgUrl) {
      $('.nav_avatar').css('background-image', 'url(' + svgUrl + ')');
    }
  
    function avatarTileHtml(avatar, clickCb) {
      var avatarTile = $('<div class="avatar-tile" data-avatar-pk="' +
        avatar.pk +
        '"><div><img src="' + avatar.avatar_url + '"></div></div>');
  
      if (avatar.active) {
        avatarTile.addClass('active');
      }
      avatarTile.click(clickCb);
      return avatarTile;
    }
  
    function appendAvatars(el, avatars, clickCb) {
      avatars.forEach((avatar) => {
        el.find('.avatars-container').append(avatarTileHtml(avatar, clickCb));
      });
      if (avatars.length > 0) {
        el.find('.empty-avatars').remove();
      }
    }
  
    function markAvatarAsActive(el) {
      $('.avatar-tile').removeClass('active');
      targetEl.addClass('active');
    }
  
  
    function selectMyAvatar(e) {
      targetEl = $(e.currentTarget);
      if (targetEl.hasClass('active')) {
        return;
      }
      var avatarToActivatePk = targetEl.data('avatar-pk');
  
      postSelection('/avatar/activate', avatarToActivatePk)
        .then((response) => {
          if (response.ok) {
            markAvatarAsActive(targetEl);
            var activatedAvatar = myAvatars.filter((avatar) => avatar.pk === avatarToActivatePk)[0];
  
            updateNavAvatar(activatedAvatar.avatar_url);
            _alert({ message: gettext('Your Avatar Has Been Changed!') }, 'success');
          } else {
            _alert('There was an error during avatar selection.', 'error');
          }
        });
    }
  
    function selectPresetAvatar(e) {
      targetEl = $(e.currentTarget);
      var avatarToSelectPk = targetEl.data('avatar-pk');
  
      postSelection('/avatar/select-preset', avatarToSelectPk)
        .then((response) => {
          if (response.ok) {
            var activatedAvatar = presetAvatars.filter((avatar) => avatar.pk === avatarToSelectPk)[0];
  
            activatedAvatar.active = true;
            updateNavAvatar(activatedAvatar.avatar_url);
            $('.avatar-tile').removeClass('active');
            $('#my-avatars .avatars-container').prepend(avatarTileHtml(activatedAvatar, selectMyAvatar));
            _alert({ message: gettext('Your Avatar Has Been Changed!') }, 'success');
          } else {
            _alert('There was an error during avatar selection.', 'error');
          }
        });
    }
  
    function loadPresetAvatars() {
      fetch('/api/v0.1/avatars?recommended_by_staff=True')
        .then((resp) => resp.json())
        .then((response) => {
          presetAvatars = response;
          appendAvatars($('#preset-avatars'), presetAvatars, selectPresetAvatar);
          presetAvatarsInitialized = true;
        })
        .catch((error) => {
          _alert('There was an error during preset avatars load.', 'error');
        });
    }
  
    function loadMyAvatars() {
      fetch('/api/v0.1/avatars?profile=' + profileId)
        .then((resp) => resp.json())
        .then((response) => {
          myAvatars = response;
          myAvatarsInitialized = true;
          appendAvatars($('#my-avatars'), myAvatars, selectMyAvatar);
        })
        .catch((error) => {
          _alert('There was an error during Your avatars load.', 'error');
        });
    }
  
    function setupTabActivationListener() {
      $('#avatar-tabs a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
        var targetTab = $(e.target).attr('href');
  
        if (targetTab === '#my-avatars-tab' && !myAvatarsInitialized) {
          loadMyAvatars();
        } else if (targetTab === '#preset-avatars-tab' && !presetAvatarsInitialized) {
          loadPresetAvatars();
        }
      });
    }
  
    setupTabActivationListener();
  
  }(profileId));