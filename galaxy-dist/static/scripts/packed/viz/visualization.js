define(["libs/underscore","mvc/data","viz/trackster/util","utils/config"],function(u,k,n,q){var f={toJSON:function(){var w=this,x={};u.each(w.constructor.to_json_keys,function(y){var z=w.get(y);if(y in w.constructor.to_json_mappers){z=w.constructor.to_json_mappers[y](z,w)}x[y]=z});return x}};var a=function(w,z,y,x){$.ajax({url:w,data:y,error:function(){alert("Grid failed")},success:function(A){Galaxy.modal.show({title:"Select datasets for new tracks",body:A,buttons:{Cancel:function(){Galaxy.modal.hide()},Add:function(){var B=[];$("input[name=id]:checked,input[name=ldda_ids]:checked").each(function(){var C={data_type:"track_config",hda_ldda:"hda"},D=$(this).val();if($(this).attr("name")!=="id"){C.hda_ldda="ldda"}B[B.length]=$.ajax({url:z+"/"+D,data:C,dataType:"json"})});$.when.apply($,B).then(function(){var C=(arguments[0] instanceof Array?$.map(arguments,function(D){return D[0]}):[arguments[0]]);x(C)});Galaxy.modal.hide()}}})}})};var l=function(w){return("promise" in w)};var g=function(w){this.default_font=w!==undefined?w:"9px Monaco, Lucida Console, monospace";this.dummy_canvas=this.new_canvas();this.dummy_context=this.dummy_canvas.getContext("2d");this.dummy_context.font=this.default_font;this.char_width_px=this.dummy_context.measureText("A").width;this.patterns={};this.load_pattern("right_strand","/visualization/strand_right.png");this.load_pattern("left_strand","/visualization/strand_left.png");this.load_pattern("right_strand_inv","/visualization/strand_right_inv.png");this.load_pattern("left_strand_inv","/visualization/strand_left_inv.png")};u.extend(g.prototype,{load_pattern:function(w,A){var x=this.patterns,y=this.dummy_context,z=new Image();z.src=galaxy_config.root+"static/images"+A;z.onload=function(){x[w]=y.createPattern(z,"repeat")}},get_pattern:function(w){return this.patterns[w]},new_canvas:function(){var w=$("<canvas/>")[0];if(window.G_vmlCanvasManager){G_vmlCanvasManager.initElement(w)}w.manager=this;return w}});var s=Backbone.Model.extend({defaults:{num_elements:20,obj_cache:null,key_ary:null},initialize:function(w){this.clear()},get_elt:function(y){var z=this.attributes.obj_cache,A=this.attributes.key_ary,x=y.toString(),w=u.indexOf(A,function(B){return B.toString()===x});if(w!==-1){if(z[x].stale){A.splice(w,1);delete z[x]}else{this.move_key_to_end(y,w)}}return z[x]},set_elt:function(y,A){var B=this.attributes.obj_cache,C=this.attributes.key_ary,x=y.toString(),z=this.attributes.num_elements;if(!B[x]){if(C.length>=z){var w=C.shift();delete B[w.toString()]}C.push(y)}B[x]=A;return A},move_key_to_end:function(x,w){this.attributes.key_ary.splice(w,1);this.attributes.key_ary.push(x)},clear:function(){this.attributes.obj_cache={};this.attributes.key_ary=[]},size:function(){return this.attributes.key_ary.length},most_recently_added:function(){return this.size()===0?null:this.attributes.key_ary[this.attributes.key_ary.length-1]}});var d=s.extend({defaults:u.extend({},s.prototype.defaults,{dataset:null,genome:null,init_data:null,min_region_size:200,filters_manager:null,data_type:"data",data_mode_compatible:function(w,x){return true},can_subset:function(w){return false}}),initialize:function(w){s.prototype.initialize.call(this);var x=this.get("init_data");if(x){this.add_data(x)}},add_data:function(w){if(this.get("num_elements")<w.length){this.set("num_elements",w.length)}var x=this;u.each(w,function(y){x.set_data(y.region,y)})},data_is_ready:function(){var z=this.get("dataset"),y=$.Deferred(),w=(this.get("data_type")==="raw_data"?"state":this.get("data_type")==="data"?"converted_datasets_state":"error"),x=new n.ServerStateDeferred({ajax_settings:{url:this.get("dataset").url(),data:{hda_ldda:z.get("hda_ldda"),data_type:w},dataType:"json"},interval:5000,success_fn:function(A){return A!=="pending"}});$.when(x.go()).then(function(A){y.resolve(A==="ok"||A==="data")});return y},search_features:function(w){var x=this.get("dataset"),y={query:w,hda_ldda:x.get("hda_ldda"),data_type:"features"};return $.getJSON(x.url(),y)},load_data:function(E,D,x,C){var A=this.get("dataset"),z={data_type:this.get("data_type"),chrom:E.get("chrom"),low:E.get("start"),high:E.get("end"),mode:D,resolution:x,hda_ldda:A.get("hda_ldda")};$.extend(z,C);var G=this.get("filters_manager");if(G){var H=[];var w=G.filters;for(var B=0;B<w.length;B++){H.push(w[B].name)}z.filter_cols=JSON.stringify(H)}var y=this,F=$.getJSON(A.url(),z,function(I){I.region=E;y.set_data(E,I)});this.set_data(E,F);return F},get_data:function(D,C,y,A){var E=this.get_elt(D);if(E&&(l(E)||this.get("data_mode_compatible")(E,C))){return E}var F=this.get("key_ary"),w=this.get("obj_cache"),x,B;for(var z=0;z<F.length;z++){x=F[z];if(x.contains(D)){B=true;E=w[x.toString()];if(l(E)||(this.get("data_mode_compatible")(E,C)&&this.get("can_subset")(E))){this.move_key_to_end(x,z);if(!l(E)){var H=this.subset_entry(E,D);this.set(D,H);E=H}return E}}}if(!B&&D.length()<this.attributes.min_region_size){D=D.copy();var G=this.most_recently_added();if(!G||(D.get("start")>G.get("start"))){D.set("end",D.get("start")+this.attributes.min_region_size)}else{D.set("start",D.get("end")-this.attributes.min_region_size)}D.set("genome",this.attributes.genome);D.trim()}return this.load_data(D,C,y,A)},set_data:function(x,w){this.set_elt(x,w)},DEEP_DATA_REQ:"deep",BROAD_DATA_REQ:"breadth",get_more_data:function(E,D,z,C,A){var G=this._mark_stale(E);if(!(G&&this.get("data_mode_compatible")(G,D))){console.log("ERROR: problem with getting more data: current data is not compatible");return}var y=E.get("start");if(A===this.DEEP_DATA_REQ){$.extend(C,{start_val:G.data.length+1})}else{if(A===this.BROAD_DATA_REQ){y=(G.max_high?G.max_high:G.data[G.data.length-1][2])+1}}var F=E.copy().set("start",y);var x=this,B=this.load_data(F,D,z,C),w=$.Deferred();this.set_data(E,w);$.when(B).then(function(H){if(H.data){H.data=G.data.concat(H.data);if(H.max_low){H.max_low=G.max_low}if(H.message){H.message=H.message.replace(/[0-9]+/,H.data.length)}}x.set_data(E,H);w.resolve(H)});return w},can_get_more_detailed_data:function(x){var w=this.get_elt(x);return(w.dataset_type==="bigwig"&&w.data.length<8000)},get_more_detailed_data:function(z,B,x,A,y){var w=this._mark_stale(z);if(!w){console.log("ERROR getting more detailed data: no current data");return}if(!y){y={}}if(w.dataset_type==="bigwig"){y.num_samples=1000*A}return this.load_data(z,B,x,y)},_mark_stale:function(x){var w=this.get_elt(x);if(!w){console.log("ERROR: no data to mark as stale: ",this.get("dataset"),x.toString())}w.stale=true;return w},get_genome_wide_data:function(w){var y=this,A=true,z=u.map(w.get("chroms_info").chrom_info,function(C){var B=y.get_elt(new h({chrom:C.chrom,start:0,end:C.len}));if(!B){A=false}return B});if(A){return z}var x=$.Deferred();$.getJSON(this.get("dataset").url(),{data_type:"genome_data"},function(B){y.add_data(B.data);x.resolve(B.data)});return x},subset_entry:function(y,z){var w={bigwig:function(A,B){return u.filter(A,function(C){return C[0]>=B.get("start")&&C[0]<=B.get("end")})},refseq:function(B,C){var D=C.get("start")-y.region.get("start"),A=y.data.length-(y.region.get("end")-C.get("end"));return y.data.slice(D,A)}};var x=y.data;if(!y.region.same(z)&&y.dataset_type in w){x=w[y.dataset_type](y.data,z)}return{region:z,data:x,dataset_type:y.dataset_type}}});var r=d.extend({initialize:function(w){var x=new Backbone.Model();x.urlRoot=w.data_url;this.set("dataset",x)},load_data:function(y,z,w,x){return(y.length()<=100000?d.prototype.load_data.call(this,y,z,w,x):{data:null,region:y})}});var c=Backbone.Model.extend({defaults:{name:null,key:null,chroms_info:null},initialize:function(w){this.id=w.dbkey},get_chroms_info:function(){return this.attributes.chroms_info.chrom_info},get_chrom_region:function(w){var x=u.find(this.get_chroms_info(),function(y){return y.chrom===w});return new h({chrom:x.chrom,end:x.len})},get_chrom_len:function(w){return u.find(this.get_chroms_info(),function(x){return x.chrom===w}).len}});var h=Backbone.Model.extend({defaults:{chrom:null,start:0,end:0,str_val:null,genome:null},same:function(w){return this.attributes.chrom===w.get("chrom")&&this.attributes.start===w.get("start")&&this.attributes.end===w.get("end")},initialize:function(x){if(x.from_str){var z=x.from_str.split(":"),y=z[0],w=z[1].split("-");this.set({chrom:y,start:parseInt(w[0],10),end:parseInt(w[1],10)})}this.attributes.str_val=this.get("chrom")+":"+this.get("start")+"-"+this.get("end");this.on("change",function(){this.attributes.str_val=this.get("chrom")+":"+this.get("start")+"-"+this.get("end")},this)},copy:function(){return new h({chrom:this.get("chrom"),start:this.get("start"),end:this.get("end")})},length:function(){return this.get("end")-this.get("start")},toString:function(){return this.attributes.str_val},toJSON:function(){return{chrom:this.get("chrom"),start:this.get("start"),end:this.get("end")}},compute_overlap:function(D){var x=this.get("chrom"),C=D.get("chrom"),B=this.get("start"),z=D.get("start"),A=this.get("end"),y=D.get("end"),w;if(x&&C&&x!==C){return h.overlap_results.DIF_CHROMS}if(B<z){if(A<z){w=h.overlap_results.BEFORE}else{if(A<y){w=h.overlap_results.OVERLAP_START}else{w=h.overlap_results.CONTAINS}}}else{if(B>z){if(B>y){w=h.overlap_results.AFTER}else{if(A<=y){w=h.overlap_results.CONTAINED_BY}else{w=h.overlap_results.OVERLAP_END}}}else{w=(A>=y?h.overlap_results.CONTAINS:h.overlap_results.CONTAINED_BY)}}return w},trim:function(w){if(this.attributes.start<0){this.attributes.start=0}if(this.attributes.genome){var x=this.attributes.genome.get_chrom_len(this.attributes.chrom);if(this.attributes.end>x){this.attributes.end=x-1}}return this},contains:function(w){return this.compute_overlap(w)===h.overlap_results.CONTAINS},overlaps:function(w){return u.intersection([this.compute_overlap(w)],[h.overlap_results.DIF_CHROMS,h.overlap_results.BEFORE,h.overlap_results.AFTER]).length===0}},{overlap_results:{DIF_CHROMS:1000,BEFORE:1001,CONTAINS:1002,OVERLAP_START:1003,OVERLAP_END:1004,CONTAINED_BY:1005,AFTER:1006}});var o=Backbone.Collection.extend({model:h});var e=Backbone.Model.extend({defaults:{region:null,note:""},initialize:function(w){this.set("region",new h(w.region))}});var t=Backbone.Collection.extend({model:e});var v=Backbone.Model.extend(f).extend({defaults:{mode:"Auto"},initialize:function(w){this.set("dataset",new k.Dataset(w.dataset));this.set("config",q.ConfigSettingCollection.from_config_dict(w.prefs));this.get("config").add([{key:"name",value:this.get("dataset").get("name")},{key:"color"}]);var x=this.get("preloaded_data");if(x){x=x.data}else{x=[]}this.set("data_manager",new d({dataset:this.get("dataset"),init_data:x}))}},{to_json_keys:["track_type","dataset","prefs","mode","filters","tool_state"],to_json_mappers:{prefs:function(x,w){if(u.size(x)===0){x={name:w.get("config").get("name").get("value"),color:w.get("config").get("color").get("value")}}return x},dataset:function(w){return{id:w.id,hda_ldda:w.get("hda_ldda")}}}});var j=Backbone.Collection.extend({model:v});var p=Backbone.Model.extend({defaults:{title:"",type:""},url:galaxy_config.root+"visualization/save",save:function(){return $.ajax({url:this.url(),type:"POST",dataType:"json",data:{vis_json:JSON.stringify(this)}})}});var m=p.extend(f).extend({defaults:u.extend({},p.prototype.defaults,{dbkey:"",drawables:null,bookmarks:null,viewport:null}),initialize:function(w){this.set("drawables",new j(w.tracks));this.set("config",q.ConfigSettingCollection.from_config_dict(w.prefs||{}));this.unset("tracks");this.get("drawables").each(function(x){x.unset("preloaded_data")})},add_tracks:function(w){this.get("drawables").add(w)}},{to_json_keys:["view","viewport","bookmarks"],to_json_mappers:{view:function(x,w){return{obj_type:"View",prefs:{name:w.get("title"),content_visible:true},drawables:w.get("drawables")}}}});var b=Backbone.Model.extend({});var i=Backbone.Router.extend({initialize:function(x){this.view=x.view;this.route(/([\w]+)$/,"change_location");this.route(/([\w]+\:[\d,]+-[\d,]+)$/,"change_location");var w=this;w.view.on("navigate",function(y){w.navigate(y)})},change_location:function(w){this.view.go_to(w)}});return{BackboneTrack:v,BrowserBookmark:e,BrowserBookmarkCollection:t,Cache:s,CanvasManager:g,Genome:c,GenomeDataManager:d,GenomeRegion:h,GenomeRegionCollection:o,GenomeVisualization:m,GenomeReferenceDataManager:r,TrackBrowserRouter:i,TrackConfig:b,Visualization:p,select_datasets:a}});