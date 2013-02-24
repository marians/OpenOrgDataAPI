<?php


/***************************************************************

  This is an interface/proxy to expose specific ElasticSearch
  search results as an API with JSON/JSONP output.

  The API supports the following URL parameters in GET
  requests:

  q - An optional search term. Returned figures deal only with
      entries matching this quer term.

  callback - This optional paramter can contain the name of a
      callback function. If this parameter is set, the output
      is returned as JSONP. Otherwise, JSON is returned.
  
  TODO:
  - Handle bad input and return corresponding HTTP status
  - Clean up response format
  - Return relative (density) figures in addition to absolute
    hit numbers. E.g. in addition to total hits in a state,
    also (a) the number of hits divided by the number of all entries
    for that state (float) should be returned. And (b) the number 
    of entries per capita (float).

  Author: Marian Steinbach

****************************************************************/

error_reporting(0);

$es_url = 'http://127.0.0.1:9200/orgdata/organisation/_search?size=0';

function do_request($url, $method, $query) {
	$params = array(
		'query' => array(
			'query_string' => array(
				'query' => 'name:' . $query
			)
		),
		'facets' => array(
			'states' => array(
				'terms' => array(
					'field' => 'state',
					'size' => 20
				)
			),
			'nameterms' => array(
				'terms' => array(
					'field' => 'name',
					'size' => 50,
					'order' => 'count'
				)
			)
		)
	);
	$params_json = json_encode($params);
	$ch = curl_init($url);
	curl_setopt($ch, CURLOPT_POST, 1);
	curl_setopt($ch, CURLOPT_POSTFIELDS, $params_json);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	$response = curl_exec($ch);
	curl_close($ch);
	return $response;
}

header('Content-type: application/json');
header('Expires: '.gmdate('D, d M Y H:i:s \G\M\T', time() + (60 * 60 * 24)));
$q = '*:*';
$jsonp = false;
$jsonp_before = '';
$jsonp_after = '';
if (isset($_GET['q']) && !empty($_GET['q'])) {
	$q = $_GET['q'];
}
if (isset($_GET['callback']) && !empty($_GET['callback'])) {
	$jsonp = true;
	$jsonp_before = $_GET['callback'] . '(';
	$jsonp_after = ')';
}
echo $jsonp_before . do_request($es_url, 'POST', $q) . $jsonp_after;

?>