// Function to add item to cart
function clicked(param) {
    // Figure out how to get the name of the table to query
      const request = new XMLHttpRequest();
      const id = param.id;
      const name = param.name
      request.open("POST", "/add_to_cart", true);

      const data = new FormData();
      data.append("id", id);
      data.append("name", name);
      var csrftoken = getCookie('csrftoken');
      request.setRequestHeader("X-CSRFToken", `${csrftoken}`);
      request.send(data);

      request.onload = () => {
        if (JSON.parse(request.responseText).toppings === 0) {
          alert("Added to cart");
        } else {
          var array = document.getElementsByClassName("plus radius");
          for (var i=0; i<array.length; i++) {
            array[i].style.display = "none";
          }
          var toppings = document.getElementsByClassName("plustop radius");
          for (var i=0; i<toppings.length; i++) {
            toppings[i].style.display = "inline-block"
          }
          alert("Added to cart, please choose your toppings");
        };
      };
      return false
};

function toppings(param) {
  // function called when a topping is added
  const request = new XMLHttpRequest();
  const id = param.id;
  const name = "topping"
  request.open("POST", "/add_to_cart", true);

  const data = new FormData();
  data.append("id", id);
  data.append("name", name);
  var csrftoken = getCookie('csrftoken');
  request.setRequestHeader("X-CSRFToken", `${csrftoken}`);
  request.send(data);

  request.onload = () => {
    if (JSON.parse(request.responseText).toppings === 0) {
      var array = document.getElementsByClassName("plus radius");
      for (var i=0; i<array.length; i++) {
        array[i].style.display = "inline-block";
      }
      var toppings = document.getElementsByClassName("plustop radius");
      for (var i=0; i<toppings.length; i++) {
        toppings[i].style.display = "none"
      }
      alert("Topping added");
    } else {
      alert("Topping added");
    };
  };
};

function remove_item(param) {
  // Removes item from menu
  const request = new XMLHttpRequest();
  const id = param.id;
  request.open("POST", "/cart", true);

  const data = new FormData();
  data.append("id", id);
  var csrftoken = getCookie('csrftoken');
  request.setRequestHeader("X-CSRFToken", `${csrftoken}`);
  request.send(data);

  request.onload = () => {
    window.location.reload(true);
  };
  return false
};

// Gets cookie for to pass as csrftoken
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            };
        };
    };
    return cookieValue;
};
