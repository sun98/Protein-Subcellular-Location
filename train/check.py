# @Author:      HgS_1217_
# @Create Date: 2018/6/23

import os
import tensorflow as tf
import numpy as np

import _import_helper

from config import CKPT_PREFIX
from data_process.data_preprocessor import generate_patch
from data_process.image_preprocessor import ImagePreprocessor

TARGET_LABELS = [0, 1, 2, 3, 4, 5]


def get_data_trainset(dataset_path):
    image_pre = ImagePreprocessor(base_dir=dataset_path, data_dir=os.path.join(dataset_path, 'testdata'))
    l1, l2, d = image_pre.get_dataset_patched(size=20, data_selection='all', label_type='int', exist='new')
    return l1, l2, d


def get_data(dataset_path):
    image_pre = ImagePreprocessor(base_dir=dataset_path, data_dir=os.path.join(dataset_path, 'testdata'))
    vals, data = image_pre.get_valset_patched(exist='new')
    data = [piece[-30:] for piece in data]
    return vals, data


def main_trainset(dataset_path):
    l1, l2, xs = get_data_trainset(dataset_path)

    ckpt = tf.train.get_checkpoint_state(CKPT_PREFIX)
    saver = tf.train.import_meta_graph(ckpt.model_checkpoint_path + '.meta')

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True

    graph = tf.get_default_graph()

    x = graph.get_operation_by_name('input_x').outputs[0]
    y = tf.get_collection('prediction')[0]
    is_training = graph.get_operation_by_name('is_training').outputs[0]
    keep_prob = graph.get_operation_by_name('keep_prob').outputs[0]

    with tf.Session(config=config) as sess:
        sess.run(tf.global_variables_initializer())
        saver.restore(sess, ckpt.model_checkpoint_path)

        results = []

        for i in range(len(xs)):
            label_array = []
            lbs = set(l1[i] + l2[i])
            for target in TARGET_LABELS:
                label_array.append([1, 0] if target in lbs else [0, 1])
            labels = np.array([label_array for _ in range(len(xs[i]))])

            pred = sess.run(y, feed_dict={x: xs[i], keep_prob: 1.0, is_training: False})
            results.append(pred)

            accu = np.mean(np.equal(np.argmax(pred, 2), np.argmax(labels, 2)), axis=0)
            print(lbs, accu, np.prod(accu))

        # print(results)


def main(dataset_path):
    vals, xs = get_data(dataset_path)

    ckpt = tf.train.get_checkpoint_state(CKPT_PREFIX)
    saver = tf.train.import_meta_graph(ckpt.model_checkpoint_path +'.meta')

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True

    graph = tf.get_default_graph()

    x = graph.get_operation_by_name('input_x').outputs[0]
    y = tf.get_collection('prediction')[0]
    is_training = graph.get_operation_by_name('is_training').outputs[0]
    keep_prob = graph.get_operation_by_name('keep_prob').outputs[0]

    with tf.Session(config=config) as sess:
        sess.run(tf.global_variables_initializer())
        saver.restore(sess, ckpt.model_checkpoint_path)

        results = {}

        for i in range(len(xs)):
            pred = sess.run(y, feed_dict={x: xs[i], keep_prob: 1.0, is_training: False})
            results[vals[i][0]] = pred

    print(results)
    with open("D:/All_Projects/py/Protein-Subcellular-Location/model/result110.csv", "w") as f:
        for val in results.keys():
            probs = ",".join([str(x[0]) for x in np.mean(results[val], axis=0).tolist()])
            res = "{0},{1}\n".format(val, probs)
            f.write(res)


if __name__ == '__main__':
    dataset_path = "D:/All_Projects/ML_project/HPA_ieee_test_new"
    # generate_patch(dataset_path)
    # main_trainset(dataset_path)
    main(dataset_path)
