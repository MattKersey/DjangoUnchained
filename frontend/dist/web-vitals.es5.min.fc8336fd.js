// modules are defined as an array
// [ module function, map of requires ]
//
// map of requires is short require name -> numeric require
//
// anything defined in a previous bundle is accessed via the
// orig method which is the require for previous bundles
parcelRequire = (function (modules, cache, entry, globalName) {
  // Save the require from previous bundle to this closure if any
  var previousRequire = typeof parcelRequire === 'function' && parcelRequire;
  var nodeRequire = typeof require === 'function' && require;

  function newRequire(name, jumped) {
    if (!cache[name]) {
      if (!modules[name]) {
        // if we cannot find the module within our internal map or
        // cache jump to the current global require ie. the last bundle
        // that was added to the page.
        var currentRequire = typeof parcelRequire === 'function' && parcelRequire;
        if (!jumped && currentRequire) {
          return currentRequire(name, true);
        }

        // If there are other bundles on this page the require from the
        // previous one is saved to 'previousRequire'. Repeat this as
        // many times as there are bundles until the module is found or
        // we exhaust the require chain.
        if (previousRequire) {
          return previousRequire(name, true);
        }

        // Try the node require function if it exists.
        if (nodeRequire && typeof name === 'string') {
          return nodeRequire(name);
        }

        var err = new Error('Cannot find module \'' + name + '\'');
        err.code = 'MODULE_NOT_FOUND';
        throw err;
      }

      localRequire.resolve = resolve;
      localRequire.cache = {};

      var module = cache[name] = new newRequire.Module(name);

      modules[name][0].call(module.exports, localRequire, module, module.exports, this);
    }

    return cache[name].exports;

    function localRequire(x){
      return newRequire(localRequire.resolve(x));
    }

    function resolve(x){
      return modules[name][1][x] || x;
    }
  }

  function Module(moduleName) {
    this.id = moduleName;
    this.bundle = newRequire;
    this.exports = {};
  }

  newRequire.isParcelRequire = true;
  newRequire.Module = Module;
  newRequire.modules = modules;
  newRequire.cache = cache;
  newRequire.parent = previousRequire;
  newRequire.register = function (id, exports) {
    modules[id] = [function (require, module) {
      module.exports = exports;
    }, {}];
  };

  var error;
  for (var i = 0; i < entry.length; i++) {
    try {
      newRequire(entry[i]);
    } catch (e) {
      // Save first error but execute all entries
      if (!error) {
        error = e;
      }
    }
  }

  if (entry.length) {
    // Expose entry point to Node, AMD or browser globals
    // Based on https://github.com/ForbesLindesay/umd/blob/master/template.js
    var mainExports = newRequire(entry[entry.length - 1]);

    // CommonJS
    if (typeof exports === "object" && typeof module !== "undefined") {
      module.exports = mainExports;

    // RequireJS
    } else if (typeof define === "function" && define.amd) {
     define(function () {
       return mainExports;
     });

    // <script>
    } else if (globalName) {
      this[globalName] = mainExports;
    }
  }

  // Override the current require with this new one
  parcelRequire = newRequire;

  if (error) {
    // throw error from earlier, _after updating parcelRequire_
    throw error;
  }

  return newRequire;
})({"../node_modules/web-vitals/dist/web-vitals.es5.min.js":[function(require,module,exports) {
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.getTTFB = exports.getLCP = exports.getFID = exports.getFCP = exports.getCLS = void 0;

var t,
    n,
    e = function () {
  return "".concat(Date.now(), "-").concat(Math.floor(8999999999999 * Math.random()) + 1e12);
},
    i = function (t) {
  var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : -1;
  return {
    name: t,
    value: n,
    delta: 0,
    entries: [],
    id: e(),
    isFinal: !1
  };
},
    a = function (t, n) {
  try {
    if (PerformanceObserver.supportedEntryTypes.includes(t)) {
      var e = new PerformanceObserver(function (t) {
        return t.getEntries().map(n);
      });
      return e.observe({
        type: t,
        buffered: !0
      }), e;
    }
  } catch (t) {}
},
    r = !1,
    o = !1,
    s = function (t) {
  r = !t.persisted;
},
    u = function () {
  addEventListener("pagehide", s), addEventListener("beforeunload", function () {});
},
    c = function (t) {
  var n = arguments.length > 1 && void 0 !== arguments[1] && arguments[1];
  o || (u(), o = !0), addEventListener("visibilitychange", function (n) {
    var e = n.timeStamp;
    "hidden" === document.visibilityState && t({
      timeStamp: e,
      isUnloading: r
    });
  }, {
    capture: !0,
    once: n
  });
},
    l = function (t, n, e, i) {
  var a;
  return function () {
    e && n.isFinal && e.disconnect(), n.value >= 0 && (i || n.isFinal || "hidden" === document.visibilityState) && (n.delta = n.value - (a || 0), (n.delta || n.isFinal || void 0 === a) && (t(n), a = n.value));
  };
},
    p = function (t) {
  var n,
      e = arguments.length > 1 && void 0 !== arguments[1] && arguments[1],
      r = i("CLS", 0),
      o = function (t) {
    t.hadRecentInput || (r.value += t.value, r.entries.push(t), n());
  },
      s = a("layout-shift", o);

  s && (n = l(t, r, s, e), c(function (t) {
    var e = t.isUnloading;
    s.takeRecords().map(o), e && (r.isFinal = !0), n();
  }));
},
    d = function () {
  return void 0 === t && (t = "hidden" === document.visibilityState ? 0 : 1 / 0, c(function (n) {
    var e = n.timeStamp;
    return t = e;
  }, !0)), {
    get timeStamp() {
      return t;
    }

  };
},
    v = function (t) {
  var n,
      e = i("FCP"),
      r = d(),
      o = a("paint", function (t) {
    "first-contentful-paint" === t.name && t.startTime < r.timeStamp && (e.value = t.startTime, e.isFinal = !0, e.entries.push(t), n());
  });
  o && (n = l(t, e, o));
},
    f = function (t) {
  var n = i("FID"),
      e = d(),
      r = function (t) {
    t.startTime < e.timeStamp && (n.value = t.processingStart - t.startTime, n.entries.push(t), n.isFinal = !0, s());
  },
      o = a("first-input", r),
      s = l(t, n, o);

  o ? c(function () {
    o.takeRecords().map(r), o.disconnect();
  }, !0) : window.perfMetrics && window.perfMetrics.onFirstInputDelay && window.perfMetrics.onFirstInputDelay(function (t, i) {
    i.timeStamp < e.timeStamp && (n.value = t, n.isFinal = !0, n.entries = [{
      entryType: "first-input",
      name: i.type,
      target: i.target,
      cancelable: i.cancelable,
      startTime: i.timeStamp,
      processingStart: i.timeStamp + t
    }], s());
  });
},
    m = function () {
  return n || (n = new Promise(function (t) {
    return ["scroll", "keydown", "pointerdown"].map(function (n) {
      addEventListener(n, t, {
        once: !0,
        passive: !0,
        capture: !0
      });
    });
  })), n;
},
    g = function (t) {
  var n,
      e = arguments.length > 1 && void 0 !== arguments[1] && arguments[1],
      r = i("LCP"),
      o = d(),
      s = function (t) {
    var e = t.startTime;
    e < o.timeStamp ? (r.value = e, r.entries.push(t)) : r.isFinal = !0, n();
  },
      u = a("largest-contentful-paint", s);

  if (u) {
    n = l(t, r, u, e);

    var p = function () {
      r.isFinal || (u.takeRecords().map(s), r.isFinal = !0, n());
    };

    m().then(p), c(p, !0);
  }
},
    h = function (t) {
  var n,
      e = i("TTFB");
  n = function () {
    try {
      var n = performance.getEntriesByType("navigation")[0] || function () {
        var t = performance.timing,
            n = {
          entryType: "navigation",
          startTime: 0
        };

        for (var e in t) "navigationStart" !== e && "toJSON" !== e && (n[e] = Math.max(t[e] - t.navigationStart, 0));

        return n;
      }();

      e.value = e.delta = n.responseStart, e.entries = [n], e.isFinal = !0, t(e);
    } catch (t) {}
  }, "complete" === document.readyState ? setTimeout(n, 0) : addEventListener("pageshow", n);
};

exports.getTTFB = h;
exports.getLCP = g;
exports.getFID = f;
exports.getFCP = v;
exports.getCLS = p;
},{}],"../node_modules/parcel-bundler/src/builtins/hmr-runtime.js":[function(require,module,exports) {
var global = arguments[3];
var OVERLAY_ID = '__parcel__error__overlay__';
var OldModule = module.bundle.Module;

function Module(moduleName) {
  OldModule.call(this, moduleName);
  this.hot = {
    data: module.bundle.hotData,
    _acceptCallbacks: [],
    _disposeCallbacks: [],
    accept: function (fn) {
      this._acceptCallbacks.push(fn || function () {});
    },
    dispose: function (fn) {
      this._disposeCallbacks.push(fn);
    }
  };
  module.bundle.hotData = null;
}

module.bundle.Module = Module;
var checkedAssets, assetsToAccept;
var parent = module.bundle.parent;

if ((!parent || !parent.isParcelRequire) && typeof WebSocket !== 'undefined') {
  var hostname = "" || location.hostname;
  var protocol = location.protocol === 'https:' ? 'wss' : 'ws';
  var ws = new WebSocket(protocol + '://' + hostname + ':' + "55466" + '/');

  ws.onmessage = function (event) {
    checkedAssets = {};
    assetsToAccept = [];
    var data = JSON.parse(event.data);

    if (data.type === 'update') {
      var handled = false;
      data.assets.forEach(function (asset) {
        if (!asset.isNew) {
          var didAccept = hmrAcceptCheck(global.parcelRequire, asset.id);

          if (didAccept) {
            handled = true;
          }
        }
      }); // Enable HMR for CSS by default.

      handled = handled || data.assets.every(function (asset) {
        return asset.type === 'css' && asset.generated.js;
      });

      if (handled) {
        console.clear();
        data.assets.forEach(function (asset) {
          hmrApply(global.parcelRequire, asset);
        });
        assetsToAccept.forEach(function (v) {
          hmrAcceptRun(v[0], v[1]);
        });
      } else if (location.reload) {
        // `location` global exists in a web worker context but lacks `.reload()` function.
        location.reload();
      }
    }

    if (data.type === 'reload') {
      ws.close();

      ws.onclose = function () {
        location.reload();
      };
    }

    if (data.type === 'error-resolved') {
      console.log('[parcel] ✨ Error resolved');
      removeErrorOverlay();
    }

    if (data.type === 'error') {
      console.error('[parcel] 🚨  ' + data.error.message + '\n' + data.error.stack);
      removeErrorOverlay();
      var overlay = createErrorOverlay(data);
      document.body.appendChild(overlay);
    }
  };
}

function removeErrorOverlay() {
  var overlay = document.getElementById(OVERLAY_ID);

  if (overlay) {
    overlay.remove();
  }
}

function createErrorOverlay(data) {
  var overlay = document.createElement('div');
  overlay.id = OVERLAY_ID; // html encode message and stack trace

  var message = document.createElement('div');
  var stackTrace = document.createElement('pre');
  message.innerText = data.error.message;
  stackTrace.innerText = data.error.stack;
  overlay.innerHTML = '<div style="background: black; font-size: 16px; color: white; position: fixed; height: 100%; width: 100%; top: 0px; left: 0px; padding: 30px; opacity: 0.85; font-family: Menlo, Consolas, monospace; z-index: 9999;">' + '<span style="background: red; padding: 2px 4px; border-radius: 2px;">ERROR</span>' + '<span style="top: 2px; margin-left: 5px; position: relative;">🚨</span>' + '<div style="font-size: 18px; font-weight: bold; margin-top: 20px;">' + message.innerHTML + '</div>' + '<pre>' + stackTrace.innerHTML + '</pre>' + '</div>';
  return overlay;
}

function getParents(bundle, id) {
  var modules = bundle.modules;

  if (!modules) {
    return [];
  }

  var parents = [];
  var k, d, dep;

  for (k in modules) {
    for (d in modules[k][1]) {
      dep = modules[k][1][d];

      if (dep === id || Array.isArray(dep) && dep[dep.length - 1] === id) {
        parents.push(k);
      }
    }
  }

  if (bundle.parent) {
    parents = parents.concat(getParents(bundle.parent, id));
  }

  return parents;
}

function hmrApply(bundle, asset) {
  var modules = bundle.modules;

  if (!modules) {
    return;
  }

  if (modules[asset.id] || !bundle.parent) {
    var fn = new Function('require', 'module', 'exports', asset.generated.js);
    asset.isNew = !modules[asset.id];
    modules[asset.id] = [fn, asset.deps];
  } else if (bundle.parent) {
    hmrApply(bundle.parent, asset);
  }
}

function hmrAcceptCheck(bundle, id) {
  var modules = bundle.modules;

  if (!modules) {
    return;
  }

  if (!modules[id] && bundle.parent) {
    return hmrAcceptCheck(bundle.parent, id);
  }

  if (checkedAssets[id]) {
    return;
  }

  checkedAssets[id] = true;
  var cached = bundle.cache[id];
  assetsToAccept.push([bundle, id]);

  if (cached && cached.hot && cached.hot._acceptCallbacks.length) {
    return true;
  }

  return getParents(global.parcelRequire, id).some(function (id) {
    return hmrAcceptCheck(global.parcelRequire, id);
  });
}

function hmrAcceptRun(bundle, id) {
  var cached = bundle.cache[id];
  bundle.hotData = {};

  if (cached) {
    cached.hot.data = bundle.hotData;
  }

  if (cached && cached.hot && cached.hot._disposeCallbacks.length) {
    cached.hot._disposeCallbacks.forEach(function (cb) {
      cb(bundle.hotData);
    });
  }

  delete bundle.cache[id];
  bundle(id);
  cached = bundle.cache[id];

  if (cached && cached.hot && cached.hot._acceptCallbacks.length) {
    cached.hot._acceptCallbacks.forEach(function (cb) {
      cb();
    });

    return true;
  }
}
},{}]},{},["../node_modules/parcel-bundler/src/builtins/hmr-runtime.js","../node_modules/web-vitals/dist/web-vitals.es5.min.js"], null)
//# sourceMappingURL=/web-vitals.es5.min.fc8336fd.js.map