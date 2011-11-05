<html>
<head>
<title> simple isk-daemon POX over HTTP client </title>
</head>
<body>
<pre>
<?php


	include("iskDaemonPOXLib.php");
	$imgdb = new ImageDB();

	// add some images
	$imgdb->addImages( array(
		array( 'id' => '1234', 'path' => '/home/rnc/DSC00011.JPG' ),
		array( 'id' => '5678', 'path' => '/home/rnc/DSC00014.JPG' ),
		array( 'id' => '9012', 'path' => '/home/rnc/DSC00019.JPG' )
	));

	// query for similar ones
	print_r($imgdb->getSimilarImages(1234,2));


?>
</pre>
</body>
</html>
