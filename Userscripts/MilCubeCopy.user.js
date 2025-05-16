// ==UserScript==
// @name         MilCubeCopy
// @namespace    http://tampermonkey.net/
// @version      0.1
// @author       eWloYW8
// @description  在百万立方网页上能复制和选中
// @match        *://milcubes.zju.edu.cn/*
// @grant        none
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';
    
    console.log("Tampermonkey script MilCubeCopy loaded!");

    document.oncontextmenu = null;
    document.onselectstart = null;
    document.oncopy = null;
    document.oncut = null;
    document.onpaste = null;
})();
