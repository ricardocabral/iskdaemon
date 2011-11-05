<html>
<head>
<title> Simple isk-daemon xml-rpc PHP client </title>
</head>
<body>
<?php

	function printXMLRPCError($r) {
		print "<br>An error occurred: ";
		print "<br>Code: " . htmlspecialchars($r->faultCode())
			. " <br>Reason: '" . htmlspecialchars($r->faultString());

	}

	include("xmlrpc.inc");
	$c=new xmlrpc_client("/RPC", "localhost", 31128);
	// Uncomment to turn debugging on:
	// $c->setDebug(1);

	// get list of defined databases
	$f=new xmlrpcmsg('getDbList',
		array()
	);
	$r=&$c->send($f);
	if(!$r->faultCode())
	{
		$v=$r->value();
		print "<br> getDBList(): " . $v->serialize();
	}
	else printXMLRPCError($r);

	// create db 1
	$f=new xmlrpcmsg('createDb',
		array(php_xmlrpc_encode(1))
	);
	$r=&$c->send($f);
	if(!$r->faultCode())
	{
		$v=$r->value();
		print "<br> createdb(1): " . $v->scalarval();
	}
	else printXMLRPCError($r);

	// add images to database
	$f=new xmlrpcmsg('addImg',
		array(	php_xmlrpc_encode(1),
			php_xmlrpc_encode(1),
			php_xmlrpc_encode('/home/rnc/DSC00010.JPG'))
	);
	$r=&$c->send($f);
	if(!$r->faultCode())
	{
		$v=$r->value();
		print "<br> addImg(...): " . $v->scalarval();
	}
	else printXMLRPCError($r);

	$f=new xmlrpcmsg('addImg',
		array(	php_xmlrpc_encode(1),
			php_xmlrpc_encode(2),
			php_xmlrpc_encode('/home/rnc/DSC00017.JPG'))
	);
	$r=&$c->send($f);
	if(!$r->faultCode())
	{
		$v=$r->value();
		print "<br> addImg(...): " . $v->scalarval();
	}
	else printXMLRPCError($r);

	// save db
	$f=new xmlrpcmsg('saveAllDbs',
		array()
	);
	$r=&$c->send($f);
	if(!$r->faultCode())
	{
		$v=$r->value();
		print "<br> saveAllDbs(): " . $v->scalarval();
	}
	else printXMLRPCError($r);


	// query for similar images
	$f=new xmlrpcmsg('queryImgID',
		array(php_xmlrpc_encode(1),
			php_xmlrpc_encode(1),
			php_xmlrpc_encode(1))
	);
	$r=&$c->send($f);
	if(!$r->faultCode())
	{
		print "<br> queryImgID(1): ";
		$v=$r->value();
		// iterating over values of an array object
		for ($i = 0; $i < $v->arraysize(); $i++)
		{
		  $pair = $v->arraymem($i);
		  print "<br> Result image id:"  . $pair->arraymem(0)->scalarval() . " ( " . $pair->arraymem(1)->scalarval() . "% )"; 
		}
	}
	else printXMLRPCError($r);

?>
</body>
</html>
