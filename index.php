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

//error_reporting(0);

$es_url = 'http://127.0.0.1:9200/orgdata/organisation/_search?size=0';
$cache_path = '/tmp/openorgdata_query_cache.dat';
$cache_ttl = 60 * 60 * 24; // 1 day

$stateIds = array(
	'Baden-Württemberg' => 'bw',
	'Bayern' => 'by',
	'Berlin' => 'be',
	'Brandenburg' => 'bb',
	'Bremen' => 'hb',
	'Hamburg' => 'hh',
	'Hessen' => 'he',
	'Mecklenburg-Vorpommern' => 'mv',
	'Niedersachsen' => 'ni',
	'Nordrhein-Westfalen' => 'nw',
	'Rheinland-Pfalz' => 'rp',
	'Saarland' => 'sl',
	'Sachsen' => 'sn',
	'Sachsen-Anhalt' => 'st',
	'Schleswig-Holstein' => 'sh',
	'Thüringen' => 'th'
);

/**
 * Send the search request to ElasticSearch
 * 
 * @param	String	$url		Base url for the elastic search API
 * @param	String	$query		Query term
 * @param	Bool	$termsFacet	Whether or not the wordcloud data should be returned
 * @return	String			JSON result
 */
function do_request($url, $query, $termsFacet=true) {
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
	if (!$termsFacet) {
		unset($params['facets']['nameterms']);
	}
	$params_json = json_encode($params);
	$ch = curl_init($url);
	curl_setopt($ch, CURLOPT_POST, 1);
	curl_setopt($ch, CURLOPT_POSTFIELDS, $params_json);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	$response = curl_exec($ch);
	curl_close($ch);
	return $response;
}

/**
 * Let's retrieve and cache the baseline figures (number of entries
 * per area unit.
 */
if (file_exists($cache_path) && filemtime($cache_path) > (time() - $cache_ttl)) {
	$stateData = unserialize(file_get_contents($cache_path));
} else {
	$baseFigs = do_request($es_url, '*', false);
	$baseFigs = json_decode($baseFigs);
	$stateData = array();
	foreach ($baseFigs->facets->states->terms as $entry) {
		$stateData[$entry->term] = $entry->count;
	}
	file_put_contents($cache_path, serialize($stateData), LOCK_EX);
	exit();
}

header('Content-type: application/json');
header('Expires: '.gmdate('D, d M Y H:i:s \G\M\T', time() + (60 * 60 * 24)));
$q = '*';
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

$json_data = do_request($es_url, $q);
$data = json_decode($json_data);
unset($data->_shards);
unset($data->hits->hits);
unset($data->facets->states->_type);
unset($data->facets->states->other);

$maxDensity = 0.0;
$minDensity = 1.0;
for ($i=0; $i<count($data->facets->states->terms); $i++) {
	$data->facets->states->terms[$i]->state_id = $stateIds[$data->facets->states->terms[$i]->term];
	$data->facets->states->terms[$i]->all = $stateData[$data->facets->states->terms[$i]->term];
	$dens = $data->facets->states->terms[$i]->count / $stateData[$data->facets->states->terms[$i]->term];
	$data->facets->states->terms[$i]->density = $dens;
	$maxDensity = max($maxDensity, $dens);
	$minDensity = min($minDensity, $dens);
}

$data->facets->states->density_min = $minDensity;
$data->facets->states->density_max = $maxDensity;

$json_data = json_encode($data);
echo $jsonp_before . $json_data . $jsonp_after;

?>