<?php

error_reporting(0);

$es_url = 'http://127.0.0.1:9200/orgdata/organisation/_search?size=0';

function do_request($url, $method, $query) {
	$params = array(
		'query' => array(
			'query_string' => array(
				'query' => $query
			)
		),
		'facets' => array(
			'states' => array(
				'terms' => array('field' => 'state')
			),
			'nameterms' => array(
				'terms' => array(
					'field' => 'name',
					'size' => 30,
					'order' => 'count'
				)
			)
		)
	);
	//$params = array(
	//	'query' => array('query_string' => array(
	//		'query' => $query
	//	))
	//);
	$params_json = json_encode($params);
	//print $params_json;
	$ch = curl_init($url);
	curl_setopt($ch, CURLOPT_POST, 1);
	curl_setopt($ch, CURLOPT_POSTFIELDS, $params_json);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	$response = curl_exec($ch);
	curl_close($ch);
	return $response;
}

header('Content-type: application/json');
$q = '*:*';
$jsonp = false;
$jsonp_before = '';
if (isset($_GET['q']) && !empty($_GET['q'])) {
	$q = $_GET['q'];
}
if (isset($_GET['callback']) && !empty($_GET['callback'])) {
	$jsonp = true;
	$jsonp_before = $_GET['callback'];
}
echo $jsonp_before.do_request($es_url, 'POST', $q);

?>