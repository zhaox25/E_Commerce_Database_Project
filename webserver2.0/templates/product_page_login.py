<!DOCTYPE html>
<html>
<style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

tr:nth-child(odd) {
  background-color: #cce0ff;
}
</style>


<body>
  <h1>Broadway Online Shopping</h1>



  <p id="greeting">Welcome! <a id="myAnchor" href=" ">  {{result_username[0]}}  </a ></p >

  <script type = "text/javaScript">   
  var j = {{result_username[0]}};
  if (j === 8888) { 
    document.getElementById("greeting").innerHTML = "Welcome Guest"; 
  } 
  </script> 

  

  <p>This is {{data[0]}} 's detailed information</p >

<table>
  <tr>
    <th>Product Name</th>
    <th>Category</th>
    <th>Brand</th>
    <th>Price</th>
    <th>Seller Name</th>
    <th>Number of Orders</th>
    <th>Average Rating</th>
    <th>Favorite</th>
  </tr>
  <tc>
    {% for result in all_product %}
                <tr>
                    <td>{{ result[0] }}</td>
                    <td>{{ result[1] }}</td>
                    <td>{{ result[2] }}</td>
                    <td style="display:none;">{{ result[3] }}</td>
                    <td>{{ result[4] }}</td>
                    <td style="display:none;">{{ result[5] }}</td>
                    <td> <a href="/seller_info?seller_id={{result[3]}}&username={{result_username[0]}}"> {{ result[6] }} </a ></td>
                    <td>{{ result[7] }}</td>
                    <td>  <a href="/review?review_pid={{result[5]}}&username={{result_username[0]}}"> {{ result[8] }} </a ></td>
                    <td> <a href="/add_favorite?favoriate_pid={{result[5]}}&username={{result_username[0]}}"> Add to Favorite </a ></td>
                </tr>
    {% endfor %}
  </tc>
</table>


<p><a id="myAnchor" href="/backtomain?un={{result_username[0]}}">Go to main page</a ></p >

<script type = "text/javaScript">   
var j = {{result_username[0]}};
if (j === 8888) { 
  document.getElementById("myAnchor").href = "/"; 
} 
</script> 

</body>

</html>