[33mcommit dab344ba08cd236ef7d910320b6f8f4e0dd7c765[m[33m ([m[1;36mHEAD -> [m[1;32mdevelopment[m[33m, [m[1;31mlunchbreak/development[m[33m)[m
Author: ks0921 <k5mks@yandex.com>
Date:   Mon Apr 1 07:21:49 2019 +0800

    change all data

[33mcommit 572e4f58b7807cf0ac7d01b05986a9dc03b93437[m[33m ([m[1;33mtag: 2.2.23[m[33m)[m
Author: Andreas Backx <andreas@backx.org>
Date:   Sat Sep 30 13:11:32 2017 +0200

    Added better handling of failed Payconiq transactions.

[33mcommit 748e5df9c2629c7c5e08685ac2d5927d705c8738[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 28 22:52:19 2017 +0200

    Editing orders does not check Store.groups_only.

[33mcommit 7380e8d1a452898aad6dbe9636ced1640336046c[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 28 21:16:28 2017 +0200

    Moved staging to APNS production environment.

[33mcommit 5dcfa53be7c2add12e209354dac3698783390e7a[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 28 20:54:53 2017 +0200

    Added groups_only to serializers.

[33mcommit f0da44a7eb03582a54daff0cb9781db85262f555[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 28 20:52:24 2017 +0200

    Added extra mock to groups only order test.

[33mcommit e69387774e33375c6faff41c2759ef5a27be31e8[m
Author: Andreas Backx <andreas@backx.org>
Date:   Wed Sep 27 17:14:57 2017 +0200

    Added email mock to test_groups_only test.

[33mcommit 0d758cb4452f85dcc48e48934cf736a252a75dfd[m
Author: Andreas Backx <andreas@backx.org>
Date:   Wed Sep 27 17:06:48 2017 +0200

    Frontend uses Store.groups_only. Fixed duplicate stores being returned.

[33mcommit 79163f46f4cba889958970b81952e122002f773d[m
Author: Andreas Backx <andreas@backx.org>
Date:   Wed Sep 27 13:11:10 2017 +0200

    Added GroupsOnly exception code 609 and added groups only order tests.

[33mcommit 0d26727405d843a98c122199637362cab26ed008[m
Author: Andreas Backx <andreas@backx.org>
Date:   Tue Sep 26 22:24:54 2017 +0200

    Added Store.groups_only with tests for customer store requests.

[33mcommit 3acc5134f89fc119b9d836a4f3209cc9afe30252[m[33m ([m[1;33mtag: 2.2.22[m[33m)[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 21 19:30:47 2017 +0200

    Added timeouts to Payconiq web app.

[33mcommit dc4aff974ef3af067c813db9e11464729aa70097[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 21 19:05:47 2017 +0200

    Web app automatically select first payment method.

[33mcommit a235e94ca925ecae6239a8a7aaa0487208dd9f29[m[33m ([m[1;33mtag: 2.2.21[m[33m)[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 21 13:38:58 2017 +0200

    Fixed issue where ingredients were not passed onto cloned OrderedFood.

[33mcommit 5935265292cbd878fa8d8875c4c37f487e966a37[m[33m ([m[1;33mtag: 2.2.20[m[33m)[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 14 00:32:35 2017 +0200

    Added business lower case login, and password reset. Resolves #177.
    
    * Added tests as well.

[33mcommit cbd1621bc8fa1d67e9e08dacd21dead381639f9c[m[33m ([m[1;33mtag: 2.2.19[m[33m)[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 7 22:09:24 2017 +0200

    Food.objects now returns deleted models and customer requests don't.

[33mcommit 9cd0c2e62b0aa39383ed77e73a4abc34b0d15cfc[m[33m ([m[1;33mtag: 2.2.18[m[33m)[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 7 16:20:47 2017 +0200

    Order DayWidget's days by date.

[33mcommit df1856205739df5b3a0481f509856483a4db1f9c[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 7 16:13:43 2017 +0200

    Order.payment_payconiq is used on the Group page.

[33mcommit 196dd82326a02a76120bce13f91222b18371633f[m[33m ([m[1;33mtag: 2.2.17[m[33m)[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 7 15:43:30 2017 +0200

    Added test and fixed #179.

[33mcommit 8fad2df0f08597174fd31009895c7bfec13cf82c[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Sep 7 15:27:57 2017 +0200

    Group page only shows confirmed orders.
    
    * Order confirmation page shows valid receipt timezone if a GroupOrder.
    * Logout link is visible on white headers.
    * Group day dropdown incorporates tokens in links.

[33mcommit d7edae1854b7b1023dd324d23991d88fe58f1d0e[m[33m ([m[1;33mtag: 2.2.16[m[33m)[m
Author: Andreas Backx <andreas@backx.org>
Date:   Wed Sep 6 13:59:25 2017 +0200

    Fixed /customers/store/recent request.

[33mcommit a408a1cda06ad511be7a8cb094cad99917076d1d[m[33m ([m[1;33mtag: 2.2.15[m[33m)[m
Author: Andreas Backx <andreas@backx.org>
Date:   Tue Sep 5 21:47:57 2017 +0200

    Added logout button on web app.

[33mcommit 3b366c1fb75f32594dd88e4aea5199c24362fb4a[m[33m ([m[1;33mtag: 2.2.14[m[33m)[m
Author: Andreas Backx <andreas@backx.org>
Date:   Mon Sep 4 17:58:51 2017 +0200

    Fixed bug for StoreQuerySet.nearby where distance > 1000.

[33mcommit a453020d61fb088a96e850b94d360a75aae56bad[m
Author: Andreas Backx <andreas@backx.org>
Date:   Mon Sep 4 09:28:26 2017 +0200

    Group page only show confirmed orders and add token to dropdown links.

[33mcommit fcc4c4368d921b7732c074f64bb9759b5bed9cca[m[33m ([m[1;33mtag: 2.2.13[m[33m)[m
Author: Andreas Backx <andreas@backx.org>
Date:   Mon Sep 4 00:04:37 2017 +0200

    Production environment use postgresql socket.

[33mcommit 62bfc8126e05808614e1228a4b4563ba3e7885c1[m
Author: Andreas Backx <andreas@backx.org>
Date:   Sun Sep 3 23:40:37 2017 +0200

    Production uses PostgreSQL.

[33mcommit 78e712faa3b73510ab97749fc4bcdec5d4617da7[m
Author: Andreas Backx <andreas@backx.org>
Date:   Sun Sep 3 18:46:47 2017 +0200

    Order.clean_receipt for group only on creation.

[33mcommit 96861eb22a94c92ad453f6103199efd97dc1fb17[m
Author: Andreas Backx <andreas@backx.org>
Date:   Sat Sep 2 01:24:12 2017 +0200

    Improved customers admin pages and performance.

[33mcommit 48ccca159b725b4b8da454205dde5292a8dfdbab[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Aug 31 13:05:12 2017 +0200

    Fixed django_gocardless.models.Merchant import.

[33mcommit 2aca76759cc1299359d08bdb5c965c3fe885fa2c[m
Author: Andreas Backx <andreas@backx.org>
Date:   Thu Aug 31 13:00:53 2017 +0200

    Fixed mixing of Payconiq and GoCardless merchant import.

[33mcommit cfb0075b94720b96df8050daab932e186b17d2c1[m
Author: Andreas Backx <andreas@backx.org>
Date:   Wed Aug 30 22:23:13 2017 +0200

    Updated nearby business URLs to be like the one for customers.

[33mcommit 4fcce75761783bce6d86a71bc63fb36f92dd3c90[m
Author: Andreas Backx <andreas@backx.org>
Date:   Wed Aug 30 19:05:49 2017 +0200

    Store requests return `preorder_time` min of all FoodType. #166
    
    FoodType migrations also set FoodType.preorder_time and not Food.preorder_time.

[33mcommit cca47027bb6d849613a0e967c3fcdc307bb93d2b[m
Author: Andreas Backx <andreas@backx.org>
Date:   Wed Aug 30 16:45:59 2017 +0200

    Business FoodType requests only return the FoodType of the store.

[33mcommit da4243a5a22a4df7780eb4ef9821ce0a3ccc4c84[m
Author: Andreas Backx <andreas@backx.org>
Date:   Wed Aug 30 13:48:59 2017 +0200

    Fixed bug in PreorderTransformation where preorder_days wasn't in the data.

[33mcommit 851b80d48df55dacd24f73835ae7507c704fc76a[m
Author: Andreas Backx <andreas@backx.org>
Date:   Tue Aug 29 23:52:33 2017 +0200

    Added forward business transformations for preorder Store and Food. #166
    
    Added tests as well.

[33mcommit c8010db7204c094876cd870c503b591557eef2a2[m
Author: Andreas Backx <andreas@backx.org>
Date:   Tue Aug 29 18:02:24 2017 +0200

    Improved preorder food transformation and added tests.

[33mcommit b332b8551885fa9601f425d210288cabd8d943eb[m
Author: Andreas Backx <andreas@backx.org>
Date:   Tue Aug 29 16:49:12 2017 +0200

    Added transformation for store preorder and fixed nearby stores request.

[33mcommit 77e31fe3e7b09fb607e40f3440592213dd37ea8e[m
Author: Andreas Backx <andreas@backx.org>
Date:   Sun Aug 27 15:47:35 2017 +0200

    PostgreSQLTransformation version set to default version.

[33mcommit 7f8c7aa8487661e4266e67646ad61c1e20a0e90c[m
Author: Andreas Backx <andreas@backx.org>
Date:   Sat