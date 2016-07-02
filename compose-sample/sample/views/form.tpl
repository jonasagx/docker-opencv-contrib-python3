<div style='height:10%'>
  <form action="/upload" method="post" enctype="multipart/form-data">
    <div class="form-group">
      <label class="control-label" for="upload">Select a image file:
      <input type="file" name="upload">
    </div>
    <div class="form-group">
        <input type="submit" value="Upload" class="btn btn-primary">
    </div>
  </form>
</div>

<div style='height:70%'>
  <div style='float:left; width: 48%;'>
    <div>
      <h3>Original</h3>
      <img src="{{original}}" width='100%'>
    </div>
    <div>
      <h3>Detect</h3>
      <img src="{{result}}" width='100%'>
    </div>
  </div>
  <div style='float:left;width:48%;'>
    <h2>Character Recognization</h2>
    <ul>
    %for l in list:
      <li style='font-size:1.5em;'>{{l}}</li>
    %end
    </ul>
  </div>
</div>