function get_max(row)
{	
	var points = row.slice();
	points.sort(function(a,b){return b-a});
	for(var i=0;i<row.length;i++)
	{
		//console.log(row[i]);
		if(row[i] == points[0])
		{
			//console.log(i);
			return i;
		}
	}
	//alert("row_max: "+points[0]);
}

function sortIndex(row)
{
	var temp = [];
	for(var i=0;i<row.length;i++)
	{
		id = get_max(row.slice());
		row[id] = -1;
		temp.push(id);
	}
	return temp;
}

function get_poi()
{
	var poi_list = {"FOOD":[1,2,3,4],"SHOP":[5,6,7,8],"DRINK":[9,10,11,12],"EXPLORE":[13,14,15,16]};
	return poi_list;
}

function get_observation_matrix()
{
	var obv = [[0,0.8,0.1,0.1],[0.7,0.2,0.1,0],[0.1,0.3,0.1,0.5],[0.6,0.1,0.3,0],[0.3,0.3,0.2,0.2],[0.1,0.5,0.4,0]];
	//console.log(obv);
	return obv;
}

function get_transition_matrix()
{
	var trans = [[0,0.1,0.7,0.2],[0,0,0.2,0.8],[0,0.3,0,0.7],[0.5,0.2,0.3,0]];
	//console.log(trans);
	return trans;
}

function poi_exists(poi_list,entry,categories)
{
	for(var key in poi_list)
		if(key == categories[entry])
			if(poi_list[key].length>0)
				return true
	return false;
}

function add_poi(poi_list,categories,entry,seq_list)
{
	for(var key in poi_list)
	{
		if(key == categories[entry])
		{
			var poi = poi_list[key][0]; 
			seq_list.push(poi);
			poi_list[key].shift();
			break;
		}
	}
}

function get_timezone()
{
	var date = new Date();
	var hr = date.getHours();
	if(hr>=0 && hr<4)
		return 1;
	else if(hr>=4 && hr<8)
		return 2;
	else if(hr>=8 && hr<12)
		return 3;
	else if(hr>=12 && hr<16)
		return 4;
	else if(hr>=16 && hr<20)
		return 5;
	
	return 6;
}

function mainly()
{
	var categories = ["FOOD","SHOP","DRINK","EXPLORE"];
	var obv = get_observation_matrix();
	var trans = get_transition_matrix();
	var t = get_timezone()
	var obv_row = obv[t-1];
	var temp = sortIndex(obv_row.slice());
	var seq_list = [];
	var poi_list = get_poi();
	for(var entry in temp)
	{
		var idx = entry;
		while(poi_exists(poi_list,idx,categories))
		{
			add_poi(poi_list,categories,idx,seq_list);
			var j = get_max(trans[idx]);
			idx = j;
		}
	}
	console.log(seq_list);
	//alert("list: "+seq_list);
}
