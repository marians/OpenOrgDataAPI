<?php

error_reporting(0);

$es_url = 'http://127.0.0.1:9200/orgdata/organisations/_search';

function do_request($url, $method, $data) {
	$ch = curl_init($url);
	curl_setopt($ch, CURLOPT_POST, 1);
	curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	$response = curl_exec($ch);
	curl_close($ch);
	return $response;
}

echo do_request($es_url, 'POST', '');

?>